import React from "react";

import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";
import { isSetsEqual, nullOrUndefined } from "./utils.jsx";
import { Job } from "./jobs_view.jsx";


export class Worker extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            worker: {}
        };
        this.onChange = this.onChange.bind(this);
    }

    componentDidMount() {
        DATA_STORE.listen(this.onChange);
        this.setState({
            worker: DATA_STORE.state.getWorker(this.props.worker_id)
        });
    }

    componentWillUnmount() {
        DATA_STORE.unlisten(this.onChange);
    }

    onChange(state) {
        this.setState({
            worker: state.getWorker(this.props.worker_id)
        });
    }

    color_for_state() {
        if (this.state.worker.state == "working") {
            return "info";
        }
        else if (this.state.worker.state == "considering") {
            return "info";
        }
        else if (this.state.worker.state == "idle") {
            return "success";
        }
        else if (this.state.worker.state == "disconnected") {
            return "danger";
        }
        return "warning";
    }

    render() {
        console.log("RW", this.state);
        return <div className={"worker"/* + (this.props.embedded ? "" : " row")*/}>
            <div className="item-name">
                {this.state.worker.id}
                <span className="text-secondary ml-1 small">({this.state.worker.address})</span>
            </div>
            <div className="item-state"><span className={"text-" + this.color_for_state()}>{this.state.worker.state}</span></div>
            {!nullOrUndefined(this.state.worker.current_job) && !this.props.embedded ?
                <div className="indent">
                    <Job job_id={this.state.worker.current_job} key={this.state.worker.current_job} embedded={true} />
                </div> : null}
        </div>;
    }
}


export class WorkersView extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            worker_ids: new Set()
        };
        this.onChange = this.onChange.bind(this);
    }

    componentDidMount() {
        DATA_STORE.listen(this.onChange);
        this.setState({
            worker_ids: new Set(Object.keys(DATA_STORE.state.workers))
        });
    }

    componentWillUnmount() {
        DATA_STORE.unlisten(this.onChange);
    }

    onChange(state) {
        var new_ids = new Set(Object.keys(state.workers));
        if (!isSetsEqual(new_ids, this.state.worker_ids)) {
            this.setState({
                worker_ids: new_ids
            });
        }
    }

    render() {
        console.log("WJV", this.state.worker_ids);
        return <>
            {[...this.state.worker_ids].sort().map(id => <Worker key={id} worker_id={id} />)}
        </>;
    }
}

