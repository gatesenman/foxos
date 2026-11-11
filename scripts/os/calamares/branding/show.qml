import QtQuick 2.15
Item {
    id: root
    anchors.fill: parent
    Rectangle { anchors.fill: parent; color: "#0b0d12" }
    Image {
        anchors.fill: parent
        source: "welcome.png"
        fillMode: Image.PreserveAspectCrop
        opacity: 0.85
    }
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 32
        text: "狐狸OS  ·  给智能体使用的桌面操作系统"
        color: "#e6e8ee"
        font.pixelSize: 18
    }
}
