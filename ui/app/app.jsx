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
            view: "networks"
        };
    }

    change_to_network = () => this.setState({view: "networks"});
    change_to_workers = () => this.setState({view: "workers"});
    change_to_jobs = () => this.setState({view: "jobs"});
    change_to_plugins = () => this.setState({view: "plugins"});

    current_view() {
        if (this.state.view == "networks") {
            return <NetworksView />
        }
        else if (this.state.view == "workers") {
            return <WorkersView />
        }
        else if (this.state.view == "jobs") {
            return <JobsView />
        }
        else if (this.state.view == "plugins") {
            return <PluginsView />
        }
    }

    render() {
        return <>
            <nav className="navbar navbar-dark bg-dark">
                <a className="navbar-brand" href="#">DNVS</a>
                <div className="btn-group" role="group">
                    <button type="button"
                            className={"btn" + (this.state.view == "networks" ? " btn-primary" : " btn-secondary")}
                            onClick={this.change_to_network} >
                        Network
                    </button>
                    <button type="button"
                            className={"btn" + (this.state.view == "workers" ? " btn-primary" : " btn-secondary")}
                            onClick={this.change_to_workers} >
                        Workers
                    </button>
                    <button type="button"
                            className={"btn" + (this.state.view == "jobs" ? " btn-primary" : " btn-secondary")}
                            onClick={this.change_to_jobs} >
                        Jobs
                    </button>
                    <button type="button"
                            className={"btn" + (this.state.view == "plugins" ? " btn-primary" : " btn-secondary")}
                            onClick={this.change_to_plugins} >
                        Plugins
                    </button>
                </div>
            </nav>
            <div className="container mt-2">
                {this.current_view()}
            </div>
        </>;
    }
}
