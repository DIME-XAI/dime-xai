import React, { Component } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default class NotificationPanel extends Component {
  constructor(props) {
    super(props);
    this.handleClose = this.handleClose.bind(this);
  }

  handleClose(event) {
    this.props.hideAppNotification();
  }

  componentDidMount() {
    const height = document.getElementById("header-notification").clientHeight;
    this.setState({ height });
  }

  render() {
    return (
      <>
        <AnimatePresence>
          <motion.div
            className="app-notification"
            id="header-notification"
            key="header-notification"
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            exit={{ y: -100 }}
          >
            <div className="app-notification-header">
              <h5
                className="app-notification-title"
                id="header-notification-title"
              >
                {this.props.notifyTitle}
              </h5>
              <button
                type="button"
                className="btn-close btn-close-white"
                onClick={this.handleClose}
                aria-label="Close"
                id="header-notification-close"
              ></button>
            </div>
            <div className="app-notification-body scroll-hidden">
              <div className="row align-items-md-stretch">
                <p id="header-notification-body">{this.props.notifyBody}</p>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </>
    );
  }
}
