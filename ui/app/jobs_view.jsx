import React from "react";


class Job extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <div className="alert alert-info">
            {this.props.job.id} - {this.props.job.state} {this.props.job.performed_by}
        </div>;
    }
}


export class JobsView extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <>
            {Object.keys(this.props.jobs).map(id => <Job key={id} job={this.props.jobs[id]} />)}
        </>;
    }
}
