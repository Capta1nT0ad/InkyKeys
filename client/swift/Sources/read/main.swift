import Foundation
import OpenMultitouchSupport

@main
struct TouchApp {
    static func main() async {
        let manager = OMSManager.shared
        manager.startListening()
        
        for await touches in manager.touchDataStream {
            if let touch = touches.first {
                let x = Double(touch.position.x)
                let y = Double(touch.position.y)
                print("\(x),\(y)")
                if touch.state == .leaving {
                    print("pass")
                }
                fflush(stdout)
            }
        }
    }
}
