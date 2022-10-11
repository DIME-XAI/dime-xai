import React from "react";
import { HashRouter as Router, Routes, Route } from "react-router-dom";
import { configs } from "./configs";
import axios from "axios";
import NotificationPanel from "./components/notificationPanel/NotificationPanel";
import Sidebar from "./components/sidebar/Sidebar";
import { dime_ascii_sm, GlobalDebug } from "./configs";
import Dashboard from "./pages/dashboard/Dashboard";
import Explanations from "./pages/explanations/Explanations";
import Models from "./pages/models/Models";
import AppLoader from "./components/loaders/AppLoader";
import Error from "./pages/error/Error";

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      appTheme: this.props.appTheme,
      appEnv: this.props.appEnv,
      sidebarActiveLink: "dashboard",
      notify: this.props.notify,
      notifyTitle: "Notification",
      notifyBody: "Hello DIME!",
      appConfigs: undefined,
      fetchingConfigsInProgress: false,
    };

    this.handleAppTheme = this.handleAppTheme.bind(this);
    this.showAppNotification = this.showAppNotification.bind(this);
    this.hideAppNotification = this.hideAppNotification.bind(this);
    this.scrollToTop = this.scrollToTop.bind(this);
    this.setActiveLink = this.setActiveLink.bind(this);
    this.fetchConfigs = this.fetchConfigs.bind(this);

    console.log(`%c ${dime_ascii_sm}`, "background: none; color: #bada55;");
    // env can be dev strict_local (debugging) or prod
    if (this.props.appEnv.toString().toLowerCase() === "prod") {
      GlobalDebug(false, true);
    }
  }

  componentDidMount() {
    this.fetchConfigs();
  }

  fetchConfigs() {
    this.setState({
      fetchingConfigsInProgress: true,
    });

    let payload = {
      responseType: "json",
    };

    axios
      .get(configs.configEndpoint, payload)
      .then(
        function (response) {
          console.log(response);
          if (response.data.status !== undefined) {
            if (response.data.status === "success") {
              this.setState({
                fetchingConfigsInProgress: false,
                appConfigs: JSON.parse(response.data.configs),
              });
            } else {
              throw new Error("Unexpected error");
            }
          } else {
            throw new Error("Unexpected response");
          }
        }.bind(this)
      )
      .catch(
        function (error) {
          console.log(error);
          if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            console.log("Failed to obtain configurations");
          } else if (error.request) {
            // The request was made but no response was received
            console.log(error.request);
            console.log("Server did not respond");
          } else {
            // Something happened in setting up the request that triggered an Error
            console.log("Error:", error.message);
            console.log("Configuration request failed");
          }

          this.setState({
            fetchingConfigsInProgress: false,
            appConfigs: undefined,
          });
        }.bind(this)
      );
  }

  handleAppTheme(event) {
    this.state.appTheme === "dark"
      ? this.setState({ appTheme: "light" })
      : this.setState({ appTheme: "dark" });
  }

  showAppNotification(notifyTitle, notifyBody) {
    console.log("triggerring notification");
    console.log(notifyTitle, notifyBody);
    this.setState({
      notify: true,
      notifyTitle: notifyTitle,
      notifyBody: notifyBody,
    });
  }

  hideAppNotification(event) {
    this.setState({ notify: false });
  }

  scrollToTop(event) {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  setActiveLink(event, linkName) {
    this.setState({
      sidebarActiveLink: linkName,
    });
  }

  render() {
    return (
      <>
        {this.state.appConfigs !== undefined ? (
          <Router>
            <input
              type="checkbox"
              id="dark-mode-switch"
              checked={this.state.appTheme !== "dark"}
              onChange={(e) => {}}
            />
            <input
              style={{ marginLeft: "350px", backgroundColor: "#3dd5f3" }}
              type="checkbox"
              id="dark-mode-switch-base"
              className="dark-mode-checkbox"
              checked={this.state.appTheme !== "dark"}
              onChange={(e) => {}}
            />
            <Sidebar
              handleAppTheme={this.handleAppTheme}
              currentTheme={this.state.appTheme}
              activeLink={this.state.sidebarActiveLink}
              setActiveLink={this.setActiveLink}
              appVersion={this.props?.appVersion}
            />
            <input
              style={{ marginLeft: "350px", backgroundColor: "#3dd5f3" }}
              type="checkbox"
              id="dark-mode-switch-main"
              className="dark-mode-checkbox"
              checked={this.state.appTheme !== "dark"}
              onChange={(e) => {}}
            />
            <div id="main" className="bg-main">
              {this.state.notify && (
                <NotificationPanel
                  hideAppNotification={this.hideAppNotification}
                  notifyTitle={this.state.notifyTitle}
                  notifyBody={this.state.notifyBody}
                />
              )}
              <div>
                <Routes>
                  <Route
                    index
                    element={
                      <Dashboard
                        appConfigs={this.state.appConfigs}
                        secureUrl={this.props.secureUrl}
                        showAppNotification={this.showAppNotification}
                        hideAppNotification={this.hideAppNotification}
                        scrollToTop={this.scrollToTop}
                        setActiveLink={this.setActiveLink}
                        appSinhala={this.props.appSinhala}
                        fetchConfigs={this.fetchConfigs}
                      />
                    }
                  />
                  <Route
                    path="explanations"
                    element={
                      <Explanations
                        appConfigs={this.state.appConfigs}
                        showAppNotification={this.showAppNotification}
                        hideAppNotification={this.hideAppNotification}
                        scrollToTop={this.scrollToTop}
                        setActiveLink={this.setActiveLink}
                      />
                    }
                  />
                  <Route
                    path="models"
                    element={
                      <Models
                        appConfigs={this.state.appConfigs}
                        showAppNotification={this.showAppNotification}
                        hideAppNotification={this.hideAppNotification}
                        scrollToTop={this.scrollToTop}
                        setActiveLink={this.setActiveLink}
                      />
                    }
                  />
                  <Route
                    path="error"
                    element={<Error setActiveLink={this.setActiveLink} />}
                  />
                  <Route
                    path="*"
                    element={<Error setActiveLink={this.setActiveLink} />}
                  />
                </Routes>
              </div>
            </div>
          </Router>
        ) : (
          <AppLoader
            fetchConfigs={this.fetchConfigs}
            status={this.state.fetchingConfigsInProgress}
          />
        )}
      </>
    );
  }
}
