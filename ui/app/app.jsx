import React from "react";
import update from 'immutability-helper';
import $ from "jquery";

import { WorkersView } from "./workers_view.jsx";
import { JobsView } from "./jobs_view.jsx";
import { NetworksView } from "./networks_view.jsx";
import { PluginsView } from "./plugins_view.jsx";
import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";


export class App extends React.Component {
  constructor(props) {
        super(props);
        this.state = {
            view: <NetworksView />,
            view_type: "networks",
            ws_connected: false
        };
        this.onChange = this.onChange.bind(this);
    }

    change_to_network = () => this.setState({view: <NetworksView />, view_type: "networks"});
    change_to_workers = () => this.setState({view: <WorkersView />, view_type: "workers"});
    change_to_jobs = () => this.setState({view: <JobsView />, view_type: "jobs"});
    change_to_plugins = () => this.setState({view: <PluginsView />, view_type: "plugins"});

    componentDidMount() {
        DATA_STORE.listen(this.onChange);
        this.setState({
            ws_connected: DATA_STORE.state.ws_connected
        });
    }

    componentWillUnmount() {
        DATA_STORE.unlisten(this.onChange);
    }

    onChange(state) {
        console.log(state)
        this.setState({
            ws_connected: state.ws_connected
        });
    }

    render() {
        return <>
            <nav className="navbar navbar-dark bg-dark">
                <a className="navbar-brand" href="#">DNVS</a>
                <div className="btn-group" role="group">
                    <button type="button"
                            className={"btn" + (this.state.view_type == "networks" ? " btn-primary" : " btn-secondary")}
                            onClick={this.change_to_network} >
                        Network
                    </button>
                    <button type="button"
                            className={"btn" + (this.state.view_type == "workers" ? " btn-primary" : " btn-secondary")}
                            onClick={this.change_to_workers} >
                        Workers
                    </button>
                    <button type="button"
                            className={"btn" + (this.state.view_type == "jobs" ? " btn-primary" : " btn-secondary")}
                            onClick={this.change_to_jobs} >
                        Jobs
                    </button>
                    <button type="button"
                            className={"btn" + (this.state.view_type == "plugins" ? " btn-primary" : " btn-secondary")}
                            onClick={this.change_to_plugins} >
                        Plugins
                    </button>
                </div>
            </nav>
            <div className="container mt-2">
                {this.state.ws_connected ? null : <div className="text-center h1 text-secondary mt-5">Not connected. Is the server running?</div>}
                {this.state.view}
            </div>
        </>;
    }
}
