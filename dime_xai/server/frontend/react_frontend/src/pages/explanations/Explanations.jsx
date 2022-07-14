import React, { Component } from 'react';
import axios from 'axios';
import ExplanationsPageTitle from '../../components/pageTitle/ExplanationsPageTitle';
import ExplanationsPageBanner from '../../components/pageBanner/ExplanationsPageBanner';
import ExplanationsContainer from '../../components/pageContent/ExplanationsContainer';
import { Box } from '@mui/system';
import { configs } from '../../configs';

export default class Explanations extends Component {
  constructor(props) {
    super(props);
    this.state = {
      fetchInProgress: false,
      explanationList: undefined,
    };

    this.fetchExplanations = this.fetchExplanations.bind(this);
  }

  componentDidMount() {
    this.props.setActiveLink("", "explanations");
    this.fetchExplanations();
  }

  fetchExplanations(event) {
    let payload = {
      models_path: this.props.appConfigs.dime_base_configs.models_path,
      origin: "explanations"
    };

    axios.post(`${configs.statsEndpoint}`, payload)
      .then(function (response) {
        console.log(response);
        if (response.data.status !== undefined) {
          if (response.data.status === "success") {
            this.setState({
              explanationList: response.data.explanations_list
            });

          } else {
            throw new Error("Unexpected error");
          }

        } else {
          throw new Error("Unexpected response");
        }

      }.bind(this))
      .catch(function (error) {
        console.log(error);
        console.log(error.config);

        this.setState({
          explanationList: undefined
        });

      }.bind(this));
  }

  render() {
    return (
      <div
        className="app-main">
        <Box className="main-section m-0 p-0" id="main-section-dashboard">
          <ExplanationsPageTitle
            showAppNotification={this.props.showAppNotification}
            hideAppNotification={this.props.hideAppNotification}
            scrollToTop={this.props.scrollToTop}
            fetchExplanations={this.fetchExplanations} />
          <ExplanationsPageBanner />
          <ExplanationsContainer
            appConfigs={this.props.appConfigs}
            showAppNotification={this.props.showAppNotification}
            hideAppNotification={this.props.hideAppNotification}
            scrollToTop={this.props.scrollToTop}
            explanationList={this.state.explanationList}
            fetchExplanations={this.fetchExplanations} />
        </Box>
      </div>
    );
  }
}
