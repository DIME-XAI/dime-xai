import React, { Component } from 'react';
import { Box, Button, DialogTitle, Drawer, Stack } from '@mui/material';
import UploadIcon from '@mui/icons-material/Upload';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import ExplanationDetails from '../explanation/ExplanationDetails';
import GlobalExplanation from '../explanation/GlobalExplanation';
import DualExplanation from '../explanation/DualExplanation';
import { ElectricBolt } from '@mui/icons-material';
import axios, { CanceledError } from 'axios';
import { configs } from '../../configs';


const Alert = React.forwardRef((props, ref) =>
  <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />
);

export default class ExplanationsPageTitle extends Component {
  constructor(props) {
    super(props);
    this.state = {
      peakFile: "",
      snackbarIsOpen: false,
      snackbarMessage: '',
      snackbarType: "success",
      drawerIsOpen: false
    };

    this.fileInput = React.createRef();

    this.handlePeak = this.handlePeak.bind(this);
    this.handleUpload = this.handleUpload.bind(this);
    this.handleSnackbarClose = this.handleSnackbarClose.bind(this);
    this.handleDrawerClose = this.handleDrawerClose.bind(this);
    this.validateExplanation = this.validateExplanation.bind(this);
  }

  handleSnackbarClose(event) {
    this.setState({ snackbarIsOpen: false });
  }

  validateExplanation(explanation) {
    const DEFAULT_DIME_EXPLANATION_BASE_KEYS = ['global', 'dual', 'config', 'timestamp', 'data', 'model', 'filename'];
    const DEFAULT_DIME_EXPLANATION_TIMESTAMP_KEYS = ['start', 'end'];
    const DEFAULT_DIME_EXPLANATION_MODEL_KEYS = ['fingerprint', 'name', 'version', 'type', 'path', 'mode', 'url'];
    const DEFAULT_DIME_EXPLANATION_DATA_KEYS = ['fingerprint', 'tokens', 'vocabulary', 'instances', 'intents', 'path'];
    const DEFAULT_DIME_EXPLANATION_CONFIG_KEYS = ['case_sensitive', 'output_mode', 'ranking_length', 'metric', 'ngrams'];
    const DEFAULT_DIME_EXPLANATION_NGRAMS_KEYS = ['min_ngrams', 'max_ngrams'];
    const DEFAULT_DIME_EXPLANATION_GLOBAL_KEYS = ['feature_importance', 'normalized_scores', 'probability_scores'];
    const DEFAULT_DIME_EXPLANATION_DUAL_KEYS = ['instance', 'global', 'dual'];
    const DEFAULT_DIME_EXPLANATION_DUAL_SUB_GLOBAL = ['feature_importance', 'feature_selection', 'normalized_scores', 'probability_scores', 'predicted_intent', 'predicted_confidence'];
    const DEFAULT_DIME_EXPLANATION_DUAL_SUB_DUAL = ['feature_importance', 'normalized_scores', 'probability_scores'];

    try {
      const base_keys = Object.keys(explanation);
      base_keys.forEach((key) => {
        if (DEFAULT_DIME_EXPLANATION_BASE_KEYS.indexOf(key) === -1) {
          console.log(`${key} is missing`);
          return false;
        }
      });

      const timestamp_keys = Object.keys(explanation.timestamp);
      timestamp_keys.forEach((key) => {
        if (DEFAULT_DIME_EXPLANATION_TIMESTAMP_KEYS.indexOf(key) === -1) {
          console.log(`${key} is missing`);
          return false;
        }
      });

      const model_keys = Object.keys(explanation.model);
      model_keys.forEach((key) => {
        if (DEFAULT_DIME_EXPLANATION_MODEL_KEYS.indexOf(key) === -1) {
          console.log(`${key} is missing`);
          return false;
        }
      });

      const data_keys = Object.keys(explanation.data);
      data_keys.forEach((key) => {
        if (DEFAULT_DIME_EXPLANATION_DATA_KEYS.indexOf(key) === -1) {
          console.log(`${key} is missing`);
          return false;
        }
      });

      const config_keys = Object.keys(explanation.config);
      config_keys.forEach((key) => {
        if (DEFAULT_DIME_EXPLANATION_CONFIG_KEYS.indexOf(key) === -1) {
          console.log(`${key} is missing`);
          return false;
        }
      });

      if (typeof (explanation.config.ngrams) === Object) {
        const ngram_keys = Object.keys(explanation.config.ngrams);
        ngram_keys.forEach((key) => {
          if (DEFAULT_DIME_EXPLANATION_NGRAMS_KEYS.indexOf(key) === -1) {
            console.log(`${key} is missing`);
            return false;
          }
        });
      }

      if (base_keys.indexOf('global') !== -1) {
        const global_keys = Object.keys(explanation.global);
        if (global_keys !== null) {
          global_keys.forEach((key) => {
            if (DEFAULT_DIME_EXPLANATION_GLOBAL_KEYS.indexOf(key) === -1) {
              console.log(`${key} is missing`);
              return false;
            }
          });
        }
      }

      if (base_keys.indexOf('dual') !== -1) {
        const dual_objects = explanation.dual;
        if (dual_objects !== null) {
          dual_objects.forEach((dual_object) => {
            const dual_keys = Object.keys(dual_object);
            dual_keys.forEach((key) => {
              if (DEFAULT_DIME_EXPLANATION_DUAL_KEYS.indexOf(key) === -1) {
                console.log(`${key} is missing`);
                return false;
              }
            });
          });
        } else {
          return false;
        }

        const dual_global_keys = Object.keys(explanation.dual[0].global);
        dual_global_keys.forEach((key) => {
          if (DEFAULT_DIME_EXPLANATION_DUAL_SUB_GLOBAL.indexOf(key) === -1) {
            console.log(`${key} is missing`);
            return false;
          }
        });

        const dual_dual_keys = Object.keys(explanation.dual[0].dual);
        dual_dual_keys.forEach((key) => {
          if (DEFAULT_DIME_EXPLANATION_DUAL_SUB_DUAL.indexOf(key) === -1) {
            console.log(`${key} is missing`);
            return false;
          }
        });

      } else {
        console.log("dual is not present");
        return false;
      }

      return true;
    } catch (err) {
      console.log(`Exception occurred while validating. ${err}`);
      return false;
    }
  }

  handlePeak(event) {
    this.props.hideAppNotification();
    const file = event.target.files[0];
    if (file !== undefined) {
      if (file.type === 'application/json') {
        const fileReader = new FileReader();
        fileReader.readAsText(file, "UTF-8");
        fileReader.onload = e => {
          const file_json = JSON.parse(e.target.result);
          console.log("e.target.result", file_json);
          // validating
          if (this.validateExplanation(file_json)) {

            // peaking
            this.setState({
              peakFile: file_json,
              drawerIsOpen: true,
            });
          } else {
            this.setState({
              snackbarMessage: "Invalid explanation JSON structure",
              snackbarType: "error",
              snackbarIsOpen: true,
              drawerIsOpen: false,
              peakFile: "",
            });
          }

        };
      } else {
        this.setState({
          snackbarMessage: "Only JSON files are allowed!",
          snackbarType: "error",
          snackbarIsOpen: true,
          drawerIsOpen: false,
          peakFile: "",
        });
      }
    } else {
      this.setState({
        drawerIsOpen: false,
        peakFile: "",
      })
    }
    event.target.value = "";
  }

  handleUpload(event) {
    this.props.hideAppNotification();
    const file = event.target.files[0];
    if (file !== undefined) {
      if (file.type === 'application/json') {
        const fileReader = new FileReader();
        fileReader.readAsText(file, "UTF-8");
        fileReader.onload = e => {
          const file_json = JSON.parse(e.target.result);
          console.log("Read the file content successfully.");
          // validating
          if (this.validateExplanation(file_json)) {

            // uploading
            let payload = {
              explanation: file_json,
            };

            axios.post(configs.explanationEndpoint, payload)
              .then(function (response) {
                console.log(response);
                if (response.data.status !== undefined) {
                  if (response.data.status === "success") {
                    let explanation = payload.explanation;
                    this.setState({
                      snackbarMessage: "Explanation uploaded successfully!",
                      snackbarType: "success",
                      snackbarIsOpen: true,
                      peakFile: explanation,
                      drawerIsOpen: true,
                    });
                    this.props.fetchExplanations();

                  } else {
                    throw new Error("Unexpected error");
                  }

                } else {
                  throw new Error("Unexpected response");
                }

              }.bind(this))
              .catch(function (error) {
                console.log(error);
                let notifyTitle = "Upload Error";
                let notifyBody = "An unknown error occurred while uploading the explanation. Please try again a bit later.";
                let snackbarMessage = "An unknown error occurred while uploading the explanation";
                let snackbarType = "error";

                if (error instanceof CanceledError) {
                  notifyBody = "Upload Request Aborted!";
                  snackbarMessage = notifyBody;
                  snackbarType = "warning";
                } else if (error.response) {
                  // The request was made and the server responded with a status code
                  // that falls out of the range of 2xx
                  notifyBody = "Failed to obtain a valid response";
                  snackbarMessage = notifyBody;
                } else if (error.request) {
                  // The request was made but no response was received
                  console.log(error.request);
                  notifyBody = "Explanation was never uploaded";
                  snackbarMessage = notifyBody;
                } else {
                  // Something happened in setting up the request that triggered an Error
                  console.log('Error:', error.message);
                  notifyBody = "Failed to upload the explanation";
                  snackbarMessage = notifyBody;
                }
                console.log(error.config);

                this.setState({
                  snackbarMessage: snackbarMessage,
                  snackbarType: snackbarType,
                  snackbarIsOpen: true,
                  explainButtonInProgress: false,
                });

                this.props.scrollToTop();
                this.props.showAppNotification(notifyTitle, notifyBody);

              }.bind(this));
          } else {
            this.setState({
              snackbarMessage: "Invalid explanation JSON structure",
              snackbarType: "error",
              snackbarIsOpen: true,
              drawerIsOpen: false,
              peakFile: "",
            });
          }
        };
      } else {
        this.setState({
          snackbarMessage: "Only JSON files are allowed!",
          snackbarType: "error",
          snackbarIsOpen: true,
          drawerIsOpen: false,
          peakFile: "",
        });
      }
    } else {
      this.setState({
        drawerIsOpen: false,
        peakFile: "",
      })
    }
    event.target.value = "";
  }

  handleDrawerClose(event) {
    this.setState({
      drawerIsOpen: false,
      peakFile: "",
    });
  }

  render() {
    return (
      <div className="row mb-1">
        <div className="col w-100 mx-0 px-0 justify-content-between d-inline-block">
          <h4 className="float-start h-100 mt-1 dime-page-title"><strong>Dual Explanations</strong></h4>
          <Stack direction="row" spacing={1} className={"float-end"}>
            <Button variant="outlined" startIcon={<ElectricBolt />}
              sx={{ border: "none", '&:hover': { border: "none" } }}
              className="float-end app-button app-button-purple mb-md-0 mb-sm-0 mx-2"
              component="label">
              Peak
              <input
                type="file"
                hidden
                accept="application/JSON"
                onChange={e => { this.handlePeak(e) }} />
            </Button>
            <Button variant="outlined" startIcon={<UploadIcon />}
              sx={{ border: "none", '&:hover': { border: "none" } }}
              className="float-end app-button app-button-green mb-md-0 mb-sm-0 mx-2"
              component="label">
              Upload
              <input
                type="file"
                hidden
                accept="application/JSON"
                onChange={e => { this.handleUpload(e) }} />
            </Button>
          </Stack>
          <Drawer
            anchor='right'
            open={this.state.drawerIsOpen}
            onClose={(e) => { this.handleDrawerClose(e) }}
            PaperProps={{ style: { width: '80%' } }}
            className={`app-explanation-drawer`}
          >
            <DialogTitle>
              <Box className="modal-header" style={{ border: "none" }}>
                <h5 className="modal-title">Explanation</h5>
                <button
                  type="button"
                  className="btn-close btn-close-white"
                  onClick={(e) => { this.handleDrawerClose(e) }}
                />
              </Box>
            </DialogTitle>
            {this.state.peakFile !== "" &&
              <Box className="w-100 row mt-4 pt-4 mb-0 model-common justify-content-center">
                <Box className="col-8 col-lg-8">
                  <ExplanationDetails data={this.state.peakFile} />
                  <GlobalExplanation color="purple" data={this.state.peakFile} />
                  <DualExplanation color="green" data={this.state.peakFile} />
                </Box>
              </Box>
            }
          </Drawer>
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
        </div>
      </div >
    );
  }
}
