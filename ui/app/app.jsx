import React from "react";

import { WorkersView } from "./workers_view.jsx";
import { JobsView } from "./jobs_view.jsx";
import { SubnetsView } from "./subnets_view.jsx";


export class App extends React.Component {
  constructor(props) {
        super(props);
        this.state = {
            view: "workers"
        };

        this.change_to_network = () => this.setState({view: "network"});
        this.change_to_workers = () => this.setState({view: "workers"});
        this.change_to_jobs = () => this.setState({view: "jobs"});
    }

    current_view() {
        if (this.state.view == "network") {
            return <SubnetsView />
        }
        else if (this.state.view == "workers") {
            return <WorkersView />
        }
        else if (this.state.view == "jobs") {
            return <JobsView />
        }
    }

    render() {
        return <>
            <nav className="navbar navbar-dark bg-dark">
                <a className="navbar-brand" href="#">DNVS</a>
                <div className="btn-group" role="group">
                    <button type="button"
                            className={"btn" + (this.state.view == "network" ? " btn-primary" : " btn-secondary")}
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
                </div>
            </nav>
            <div className="container mt-2">
                {this.current_view()}
            </div>
        </>;
    }
}
