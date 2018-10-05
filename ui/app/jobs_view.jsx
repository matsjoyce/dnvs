import React from "react";

import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";
import { isSetsEqual, nullOrUndefined } from "./utils.jsx";
import { Worker } from "./workers_view.jsx";


export class Job extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            job: {}
        };
        this.onChange = this.onChange.bind(this);
    }

    componentDidMount() {
        DATA_STORE.listen(this.onChange);
        this.setState({
            job: DATA_STORE.state.getJob(this.props.job_id)
        });
    }

    componentWillUnmount() {
        DATA_STORE.unlisten(this.onChange);
    }

    onChange(state) {
        this.setState({
            job: state.getJob(this.props.job_id)
        });
    }

    color_for_state() {
        if (this.state.job.state == "finished") {
            return "success";
        }
        else if (this.state.job.state == "running") {
            return "info";
        }
        else if (this.state.job.state == "pending") {
            return "secondary";
        }
        else if (this.state.job.state == "failed") {
            return "danger";
        }
        return "warning";
    }

    render() {
        console.log("RJ", this.state.job);
        return <div className={"job"/* + (this.props.embedded ? "" : " row")*/}>
            <div className="item-name">{this.state.job.id}</div>
            <div className="item-state"><span className={"text-" + this.color_for_state()}>{this.state.job.state}</span></div>
            {!nullOrUndefined(this.state.job.performed_by) && !this.props.embedded ?
                <div className="indent">
                    <Worker worker_id={this.state.job.performed_by} key={this.state.job.performed_by} embedded={true} />
                </div> : null}
        </div>;
    }
}


export class JobsView extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            job_ids: new Set()
        };
        this.onChange = this.onChange.bind(this);
    }

    componentDidMount() {
        DATA_STORE.listen(this.onChange);
        this.setState({
            job_ids: new Set(Object.keys(DATA_STORE.state.jobs))
        });
    }

    componentWillUnmount() {
        DATA_STORE.unlisten(this.onChange);
    }

    onChange(state) {
        var new_ids = new Set(Object.keys(state.jobs));
        if (!isSetsEqual(new_ids, this.state.job_ids)) {
            this.setState({
                job_ids: new_ids
            });
        }
    }

    render() {
        console.log("RJV", this.state.job_ids);
        return <>
            {[...this.state.job_ids].sort().map(id => <Job key={id} job_id={id} />)}
        </>;
    }
}
