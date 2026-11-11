cask "foxos" do
  arch arm: "arm64", intel: "x64"

  version "0.3.2"
  sha256 arm:   "37b253b6370f4a3c32eda89bf1c08b90bb5fbefea3c00d61867b601d6c2c2192",
         intel: "ae365285948da95cbafc7e0473380f8319a5e34d4fe4374f2a964d652fa4df48"

  url "https://github.com/gatesenman/foxos/releases/download/v0.3.2-os-preview/FoxOS-#{version}-mac-#{arch}.zip"
  name "FoxOS"
  name "狐狸OS"
  desc "FoxOS desktop companion and foxos CLI for agents (bundled Python 3.12 and kernel)"
  homepage "https://github.com/gatesenman/foxos"

  livecheck do
    url :url
    strategy :github_releases
  end

  depends_on macos: ">= :big_sur"

  app "FoxOS.app"
  binary "#{appdir}/FoxOS.app/Contents/Resources/bin/foxos"

  zap trash: [
    "~/Library/Application Support/FoxOS",
    "~/Library/Logs/FoxOS",
    "~/Library/Preferences/io.github.gatesenman.foxos.plist",
  ]

  caveats <<~EOS
    FoxOS is not notarized by Apple yet. If macOS blocks the first launch, run:
      xattr -dr com.apple.quarantine "#{appdir}/FoxOS.app"
  EOS
end
