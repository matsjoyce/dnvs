import React from "react";

import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";
import { isSetsEqual, nullOrUndefined, withDefault } from "./utils.jsx";


export class Item extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            data: {},
            expanded: withDefault(this.props.initial_expanded, false),
            collapseable: withDefault(this.props.collapseable, true)
        };
        this.onChange = this.onChange.bind(this);
    }

    expand = () => this.setState({expanded: true});
    collapse = () => this.setState({expanded: !this.state.collapseable});
    idFormat = x => "#" + x;

    componentDidMount() {
        DATA_STORE.listen(this.onChange);
        this.setState({
            data: this.getValue(DATA_STORE.state)
        });
    }

    componentWillUnmount() {
        DATA_STORE.unlisten(this.onChange);
    }

    onChange(state) {
        this.setState({
            data: this.getValue(state)
        });
    }

    color_for_state() {
        return "warning";
    }

    renderExpanded() {
        return null;
    }

    renderCollapsed() {
        return <span className={"item-collapsed text-" + this.color_for_state()} onClick={this.expand}>{this.idFormat(this.state.data.id)}</span>
    }

    render() {
        return this.state.expanded ? this.renderExpanded() : this.renderCollapsed();
    }
}


export class ItemTable extends React.PureComponent {
    render() {
        return <table><tbody>{this.props.children}</tbody></table>;
    }
}


export class ItemTableRow extends React.PureComponent {
    render() {
        if (nullOrUndefined(this.props.value)) return null;
        return <tr>
            <td className="text-secondary pr-2">{this.props.name + ":"}</td>
            <td>{this.props.value}</td>
        </tr>;
    }
}
