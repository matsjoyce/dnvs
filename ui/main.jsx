import React from "react";
import ReactDOM from "react-dom";
import $ from "jquery";
import "bootstrap";

import "./theming/main.scss"
import { App } from "./app/app.jsx";

$(document).ready(() => ReactDOM.render(<App />, document.getElementById("root")));
