// foxos-vz：狐狸OS 在 macOS 上的环境小助手，基于系统自带的 Virtualization.framework。
// 构建：swiftc -O FoxVZ.swift -o foxos-vz -framework Virtualization
//       codesign --force --entitlements foxvz.entitlements -s - foxos-vz   （需要 com.apple.security.virtualization）
// 用法：foxos-vz run --config <env>/vm.json                      Linux 轻量虚拟机
//       foxos-vz install-macos --dir D --disk-gb N [--share SEED] [--ipsw FILE]
//                                                                 下载 Apple 官方 IPSW（VZMacOSRestoreImage.fetchLatestSupported）并安装 macOS
//       foxos-vz run-macos --dir D [--share SEED]                 启动装好的 macOS（窗口；SEED 以 virtio-fs 标签 foxos-seed 共享）
// macOS 来宾只在 Apple 芯片的 Mac 上可用（Apple 许可与 Virtualization.framework 的限制）。
import Foundation
import Virtualization

struct Share: Codable { let tag: String; let path: String; let readOnly: Bool }
struct Config: Codable {
  let name: String; let cpus: Int; let memoryBytes: UInt64
  let kernel: String; let initrd: String; let commandLine: String; let disk: String
  let shares: [Share]; let network: String; let serialLog: String
}

func fail(_ msg: String) -> Never { FileHandle.standardError.write((msg + "\n").data(using: .utf8)!); exit(1) }

let args = CommandLine.arguments
func opt(_ name: String) -> String? { if let i = args.firstIndex(of: name), i + 1 < args.count { return args[i + 1] }; return nil }
if args.count >= 2 && (args[1] == "install-macos" || args[1] == "run-macos") {
#if arch(arm64)
  macosMain(install: args[1] == "install-macos")
#else
  fail("macOS guests need an Apple silicon Mac")
#endif
}
guard args.count >= 4, args[1] == "run", args[2] == "--config" else { fail("usage: foxos-vz run --config vm.json") }
guard let data = FileManager.default.contents(atPath: args[3]),
      let cfg = try? JSONDecoder().decode(Config.self, from: data) else { fail("cannot read config") }

let boot = VZLinuxBootLoader(kernelURL: URL(fileURLWithPath: cfg.kernel))
boot.initialRamdiskURL = URL(fileURLWithPath: cfg.initrd)
boot.commandLine = cfg.commandLine

let vm = VZVirtualMachineConfiguration()
vm.bootLoader = boot
vm.cpuCount = max(VZVirtualMachineConfiguration.minimumAllowedCPUCount, min(cfg.cpus, VZVirtualMachineConfiguration.maximumAllowedCPUCount))
vm.memorySize = max(VZVirtualMachineConfiguration.minimumAllowedMemorySize, min(cfg.memoryBytes, VZVirtualMachineConfiguration.maximumAllowedMemorySize))

do {
  let disk = try VZDiskImageStorageDeviceAttachment(url: URL(fileURLWithPath: cfg.disk), readOnly: false)
  vm.storageDevices = [VZVirtioBlockDeviceConfiguration(attachment: disk)]
} catch { fail("disk: \(error)") }

if cfg.network == "nat" {
  let net = VZVirtioNetworkDeviceConfiguration()
  net.attachment = VZNATNetworkDeviceAttachment()
  vm.networkDevices = [net]
}

vm.directorySharingDevices = cfg.shares.map { s in
  let dev = VZVirtioFileSystemDeviceConfiguration(tag: s.tag)
  dev.share = VZSingleDirectoryShare(directory: VZSharedDirectory(url: URL(fileURLWithPath: s.path), readOnly: s.readOnly))
  return dev
}

FileManager.default.createFile(atPath: cfg.serialLog, contents: nil)
let log = FileHandle(forWritingAtPath: cfg.serialLog)!
let console = VZVirtioConsoleDeviceSerialPortConfiguration()
console.attachment = VZFileHandleSerialPortAttachment(fileHandleForReading: FileHandle.standardInput, fileHandleForWriting: log)
vm.serialPorts = [console]
vm.entropyDevices = [VZVirtioEntropyDeviceConfiguration()]
vm.memoryBalloonDevices = [VZVirtioTraditionalMemoryBalloonDeviceConfiguration()]

do { try vm.validate() } catch { fail("invalid configuration: \(error)") }

let machine = VZVirtualMachine(configuration: vm)
signal(SIGTERM, SIG_IGN)
let term = DispatchSource.makeSignalSource(signal: SIGTERM, queue: .main)
term.setEventHandler { try? machine.requestStop() ; DispatchQueue.main.asyncAfter(deadline: .now() + 10) { exit(0) } }
term.resume()
machine.start { result in
  if case let .failure(err) = result { fail("start: \(err)") }
  print("running \(cfg.name)")
}
RunLoop.main.run()

#if arch(arm64)
// ---- macOS 来宾 ----
func macConfig(dir: URL, hw: VZMacHardwareModel, mid: VZMacMachineIdentifier, cpus: Int, mem: UInt64, share: String?) throws -> VZVirtualMachineConfiguration {
  let platform = VZMacPlatformConfiguration()
  platform.hardwareModel = hw
  platform.machineIdentifier = mid
  platform.auxiliaryStorage = VZMacAuxiliaryStorage(url: dir.appendingPathComponent("aux.img"))
  let c = VZVirtualMachineConfiguration()
  c.platform = platform
  c.bootLoader = VZMacOSBootLoader()
  c.cpuCount = max(VZVirtualMachineConfiguration.minimumAllowedCPUCount, min(cpus, VZVirtualMachineConfiguration.maximumAllowedCPUCount))
  c.memorySize = max(VZVirtualMachineConfiguration.minimumAllowedMemorySize, min(mem, VZVirtualMachineConfiguration.maximumAllowedMemorySize))
  let g = VZMacGraphicsDeviceConfiguration()
  g.displays = [VZMacGraphicsDisplayConfiguration(widthInPixels: 1920, heightInPixels: 1200, pixelsPerInch: 110)]
  c.graphicsDevices = [g]
  c.storageDevices = [VZVirtioBlockDeviceConfiguration(attachment: try VZDiskImageStorageDeviceAttachment(url: dir.appendingPathComponent("disk.img"), readOnly: false))]
  let net = VZVirtioNetworkDeviceConfiguration(); net.attachment = VZNATNetworkDeviceAttachment(); c.networkDevices = [net]
  c.pointingDevices = [VZMacTrackpadConfiguration()]
  c.keyboards = [VZMacKeyboardConfiguration()]
  c.entropyDevices = [VZVirtioEntropyDeviceConfiguration()]
  if let s = share {
    let dev = VZVirtioFileSystemDeviceConfiguration(tag: "foxos-seed")
    dev.share = VZSingleDirectoryShare(directory: VZSharedDirectory(url: URL(fileURLWithPath: s), readOnly: true))
    c.directorySharingDevices = [dev]
  }
  try c.validate()
  return c
}

var keepAlive: NSKeyValueObservation?
func say(_ s: String) { print(s); fflush(stdout) }

func macosMain(install: Bool) -> Never {
  guard let d = opt("--dir") else { fail("--dir is required") }
  let dir = URL(fileURLWithPath: d, isDirectory: true)
  try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
  let share = opt("--share")
  let cpus = Int(opt("--cpus") ?? "4") ?? 4
  let mem = (UInt64(opt("--memory-mb") ?? "8192") ?? 8192) * 1024 * 1024
  let hwURL = dir.appendingPathComponent("hardware-model.bin"), midURL = dir.appendingPathComponent("machine-id.bin")
  if !install {
    guard let hd = try? Data(contentsOf: hwURL), let hw = VZMacHardwareModel(dataRepresentation: hd),
          let md = try? Data(contentsOf: midURL), let mid = VZMacMachineIdentifier(dataRepresentation: md) else { fail("not installed: \(d)") }
    do {
      let vm = VZVirtualMachine(configuration: try macConfig(dir: dir, hw: hw, mid: mid, cpus: cpus, mem: mem, share: share))
      DispatchQueue.main.async { vm.start { r in if case let .failure(e) = r { fail("start: \(e)") }; say("running macOS") } }
      RunLoop.main.run()
    } catch { fail("config: \(error)") }
    exit(0)
  }
  let diskGB = UInt64(opt("--disk-gb") ?? "64") ?? 64
  func installFrom(_ ipsw: URL) {
    VZMacOSRestoreImage.load(from: ipsw) { res in
      switch res {
      case .failure(let e): fail("ipsw: \(e)")
      case .success(let img):
        guard let req = img.mostFeaturefulSupportedConfiguration, req.hardwareModel.isSupported else { fail("this Mac cannot run the macOS in this IPSW") }
        do {
          try req.hardwareModel.dataRepresentation.write(to: hwURL)
          let mid = VZMacMachineIdentifier(); try mid.dataRepresentation.write(to: midURL)
          _ = try VZMacAuxiliaryStorage(creatingStorageAt: dir.appendingPathComponent("aux.img"), hardwareModel: req.hardwareModel, options: [.allowOverwrite])
          let diskURL = dir.appendingPathComponent("disk.img")
          FileManager.default.createFile(atPath: diskURL.path, contents: nil)
          let fh = try FileHandle(forWritingTo: diskURL); try fh.truncate(atOffset: diskGB * 1024 * 1024 * 1024); try fh.close()
          let cfg = try macConfig(dir: dir, hw: req.hardwareModel, mid: mid, cpus: max(cpus, req.minimumSupportedCPUCount), mem: max(mem, req.minimumSupportedMemorySize), share: share)
          DispatchQueue.main.async {
            let vm = VZVirtualMachine(configuration: cfg)
            let inst = VZMacOSInstaller(virtualMachine: vm, restoringFromImageAt: ipsw)
            let obs = inst.progress.observe(\.fractionCompleted) { p, _ in say(String(format: "install %.1f%%", p.fractionCompleted * 100)) }
            inst.install { r in
              obs.invalidate()
              if case let .failure(e) = r { fail("install: \(e)") }
              say("FOXOS-MACOS-INSTALLED \(dir.path)"); exit(0)
            }
          }
        } catch { fail("prepare: \(error)") }
      }
    }
  }
  if let local = opt("--ipsw") {
    installFrom(URL(fileURLWithPath: local))
  } else {
    VZMacOSRestoreImage.fetchLatestSupported { res in
      switch res {
      case .failure(let e): fail("fetch latest: \(e)")
      case .success(let img):
        let dest = dir.appendingPathComponent("restore.ipsw")
        if FileManager.default.fileExists(atPath: dest.path) { say("ipsw cached"); installFrom(dest); return }
        say("ipsw \(img.url.absoluteString) build \(img.buildVersion)")
        let task = URLSession.shared.downloadTask(with: img.url) { tmp, _, err in
          guard let tmp = tmp, err == nil else { fail("download: \(String(describing: err))") }
          do { try FileManager.default.moveItem(at: tmp, to: dest) } catch { fail("move: \(error)") }
          installFrom(dest)
        }
        keepAlive = task.progress.observe(\.fractionCompleted) { p, _ in say(String(format: "download %.1f%%", p.fractionCompleted * 100)) }
        task.resume()
      }
    }
  }
  RunLoop.main.run()
  exit(0)
}
#endif
