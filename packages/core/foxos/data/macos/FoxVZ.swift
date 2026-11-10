// foxos-vz：狐狸OS 在 macOS 上的环境小助手，基于系统自带的 Virtualization.framework。
// 构建：swiftc -O FoxVZ.swift -o foxos-vz -framework Virtualization
//       codesign --entitlements foxvz.entitlements -s - foxos-vz   （需要 com.apple.security.virtualization）
// 用法：foxos-vz run --config <env>/vm.json
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
