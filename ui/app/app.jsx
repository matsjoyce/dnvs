import React from "react";
import update from 'immutability-helper';
import $ from "jquery";

import { WorkersView } from "./workers_view.jsx";
import { JobsView } from "./jobs_view.jsx";
import { SubnetsView } from "./subnets_view.jsx";
import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";


export class App extends React.Component {
  constructor(props) {
        super(props);
        this.state = {
            view: "jobs"
        };
    }

    change_to_network = () => this.setState({view: "network"});
    change_to_workers = () => this.setState({view: "workers"});
    change_to_jobs = () => this.setState({view: "jobs"});

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
/*
    connect_ws() {
        this.websocket = new WebSocket("ws://" + window.location.host + "/api/ws/broadcast");
        this.websocket.onmessage = this.on_ws_message.bind(this);
//         this.websocket.onclose = this.on_ws_close.bind(this);
    }

    load_initial_data() {
        $.getJSON("/api/worker").then(data => {
            var workers = {};
            data.data.workers.map(worker => workers[worker.id] = worker);
            this.setState({
                workers: workers
            })
        });
        $.getJSON("/api/job").then(data => {
            var jobs = {};
            data.data.jobs.map(job => jobs[job.id] = job);
            this.setState({
                jobs: jobs
            })
        });
    }

    on_ws_message(message) {
        var data = JSON.parse(message.data);
        if (data.type == "worker") {
            this.setState({
                workers: update(this.state.workers, {[data.data.id]: {
                    $set: data.data
                }})
            })
        }
        else if (data.type == "job") {
            this.setState({
                jobs: update(this.state.jobs, {[data.data.id]: {
                    $set: data.data
                }})
            })
        }
        else {
            console.log(data)
        }
    }

    componentDidMount() {
        this.load_initial_data();
        this.connect_ws();
    }*/

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
