import React from 'react';


class Luckysheet extends React.Component {

    constructor() {
        super()
        this.luckysheet = null
    }

    componentDidMount() {
        if (this.luckysheet)
            return

        const luckysheet = window.luckysheet;
        const wsProtocol = {
            "http:": "ws",
            "https:": "wss",
        }[window.location.protocol]

        const config = {
            container: "luckysheet",
            plugins:['chart'],
            allowUpdate: true,
            updateUrl: `ws://localhost:8080/ws/sheet-edit`,
            loadUrl: "api/sheets",
            gridKey: "__set_dynamicall__"
        }

        luckysheet.create(config);
        this.luckysheet = luckysheet
    }

    render() {
        const luckyCss = {
            margin: '0px',
            padding: '0px',
            position: 'absolute',
            width: '100%',
            height: '100%',
            left: '0px',
            top: '0px'
        }

        return (
            <div id="luckysheet" style={luckyCss}></div>
        )
    }
}

export default Luckysheet
