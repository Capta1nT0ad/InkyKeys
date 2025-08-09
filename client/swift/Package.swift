// swift-tools-version:6.0
import PackageDescription

let package = Package(
    name: "InkyKeys",
    platforms: [
        .macOS(.v13)
    ],
    dependencies: [
        .package(url: "https://github.com/krishkrosh/OpenMultitouchSupport.git", from: "1.0.12")
    ],
    targets: [
        .executableTarget(
            name: "read",
            dependencies: ["OpenMultitouchSupport"]
        )
    ]
)
