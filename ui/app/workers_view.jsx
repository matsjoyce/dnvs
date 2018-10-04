import React from "react";


class Worker extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <div className="alert alert-info">
            {this.props.worker.id} - {this.props.worker.state} {this.props.worker.current_job}
        </div>;
    }
}


export class WorkersView extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <>
            {Object.keys(this.props.workers).map(id => <Worker key={id} worker={this.props.workers[id]} />)}
        </>;
    }
}

