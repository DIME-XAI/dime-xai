import React, { Component } from "react";
import ModelsPageTitle from "../../components/pageTitle/ModelsPageTitle";
import ModelsPageBanner from "../../components/pageBanner/ModelsPageBanner";
import ModelsContainer from "../../components/pageContent/ModelsContainer";

export default class Models extends Component {
  componentDidMount() {
    this.props.setActiveLink("", "models");
  }

  render() {
    return (
      <div className="app-main">
        <div className="main-section m-0 p-0" id="main-section-dashboard">
          <ModelsPageTitle />
          <ModelsPageBanner />
          <ModelsContainer
            appConfigs={this.props.appConfigs}
            showAppNotification={this.props.showAppNotification}
            hideAppNotification={this.props.hideAppNotification}
            scrollToTop={this.props.scrollToTop}
          />
        </div>
      </div>
    );
  }
}
