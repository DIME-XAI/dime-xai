import React, { Component } from 'react';
import { Divider, List } from '@mui/material';
import axios, { CanceledError } from 'axios';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import { configs } from '../../configs';
import ModelPaginator from './ModelPaginator';


const Alert = React.forwardRef((props, ref) =>
  <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />
);

export default class ModelList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      snackbarIsOpen: false,
      snackbarMessage: '',
      snackbarType: "success",
      deleteInProgress: false,
      modelList: undefined
    };

    this.handleDelete = this.handleDelete.bind(this);
    this.handleSnackbarClose = this.handleSnackbarClose.bind(this);
    this.generateModalId = this.generateModalId.bind(this);
    this.fetchModels = this.fetchModels.bind(this);
  }

  componentDidMount() {
    this.fetchModels();
  }

  handleSnackbarClose(event) {
    this.setState({ snackbarIsOpen: false });
  }

  fetchModels(event) {
    let payload = {
      models_path: this.props.appConfigs.dime_base_configs.models_path,
      origin: "models"
    };

    axios.post(`${configs.statsEndpoint}`, payload)
      .then(function (response) {
        console.log(response);
        if (response.data.status !== undefined) {
          if (response.data.status === "success") {
            this.setState({
              modelList: response.data.models_list
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
          modelList: undefined
        });

      }.bind(this));
  }

  generateModalId(modelName) {
    try {
      modelName = modelName.replace(".tar.gz", "");
      modelName = modelName.replace(/[#_~`@$%^&*()\-+=/\\. ,?"':;]/g, "");
      return `modelid${modelName}`;
    } catch (err) {
      console.log("Exception occurred while generating Model ID")
      return "";
    }
  }

  handleDelete(event, model) {
    this.props.hideAppNotification();
    this.setState({ deleteInProgress: true });
    console.log('delete called ' + model);

    let payload = {
      headers: {
        'Content-Type': 'application/json'
      },
      data: {
        model_name: model,
        models_path: this.props.appConfigs.dime_base_configs.models_path,
      }
    };
    axios.delete(configs.modelEndpoint, payload)
      .then(function (response) {
        console.log(response);
        if (response.data.status !== undefined) {
          if (response.data.status === "success") {
            this.setState({
              snackbarMessage: "Model deleted successfully!",
              snackbarType: "success",
              snackbarIsOpen: true,
              deleteInProgress: false,
            });
            this.fetchModels();

          } else {
            throw new Error("Unexpected error");
          }

        } else {
          throw new Error("Unexpected response");
        }

      }.bind(this))
      .catch(function (error) {
        console.log(error);
        let notifyTitle = "Model Error";
        let notifyBody = `An unknown error occurred while attempting to delete the model specified (${model}). Please try again a bit later.`;
        let snackbarMessage = "An unknown error occurred while deleting the model";
        let snackbarType = "error";

        if (error instanceof CanceledError) {
          notifyBody = "Model Delete Request Aborted!";
          snackbarMessage = notifyBody;
          snackbarType = "warning";
        } else if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          notifyBody = "Failed to obtain a valid model status";
          snackbarMessage = notifyBody;
        } else if (error.request) {
          // The request was made but no response was received
          console.log(error.request);
          notifyBody = "Server did not respond";
          snackbarMessage = notifyBody;
        } else {
          // Something happened in setting up the request that triggered an Error
          console.log('Error:', error.message);
          notifyBody = "Model delete request failed";
          snackbarMessage = notifyBody;
        }
        console.log(error.config);

        this.setState({
          snackbarMessage: snackbarMessage,
          snackbarType: snackbarType,
          snackbarIsOpen: true,
          deleteInProgress: false,
        });

        this.props.scrollToTop();
        this.props.showAppNotification(notifyTitle, notifyBody);

      }.bind(this));
  }

  render() {
    return (
      <>
        <List
          sx={{ width: '100%' }}
          className="app-model-list"
          component="nav">
          <Divider component="li" variant='fullWidth' />
          {this.state.modelList !== undefined ?
            <ModelPaginator
              modelList={this.state.modelList}
              generateModalId={this.generateModalId}
              handleDelete={this.handleDelete}
              compatibilityChip={false}
              perPageItems={4}
            />
            :
            <div className='p-3'>
              Currently there are no Trained Models Available
            </div>
          }
        </List>
        <Snackbar
          open={this.state.snackbarIsOpen}
          autoHideDuration={3000}
          onClose={this.handleSnackbarClose}
          anchorOrigin={{ vertical: `${configs.snackbarVerticalPosition}`, horizontal: `${configs.snackbarHorizontalPostion}` }}>
          <Alert
            onClose={this.handleSnackbarClose}
            severity={this.state.snackbarType}
            sx={{ width: '100%' }}>
            {this.state.snackbarMessage.toString()}
          </Alert>
        </Snackbar>
      </>
    );
  }
}
