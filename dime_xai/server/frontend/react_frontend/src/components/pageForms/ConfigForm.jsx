import React, { Component } from 'react';
import { Box, Button, FormControlLabel, Menu, MenuItem, Radio, RadioGroup, Slider, Stack, TextField } from '@mui/material';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import { KeyboardArrowDown, RestartAlt, Save } from '@mui/icons-material';
import { LoadingButton } from '@mui/lab';
import axios from 'axios';
import { configs } from '../../configs';

const Alert = React.forwardRef((props, ref) =>
  <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />
);

export default class ConfigForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      snackbarIsOpen: false,
      snackbarMessage: '',
      snackbarType: "success",
      modelDropDownAnchor: null,
      modelDropDownOpen: false,
      saveInProgress: false,
      configs: {
        data_path: props.appConfigs.dime_base_configs.data_path,
        models_path: props.appConfigs.dime_base_configs.models_path,
        model_name: "Latest",
        model_mode: props.appConfigs.dime_base_configs.model_mode,
        url_endpoint: props.appConfigs.dime_base_configs.url_endpoint,
        ranking_length: props.appConfigs.dime_base_configs.ranking_length,
        case_sensitive: props.appConfigs.dime_base_configs.case_sensitive,
      },
      previousConfigs: {
        data_path: props.appConfigs.dime_base_configs.data_path,
        models_path: props.appConfigs.dime_base_configs.models_path,
        model_name: "Latest",
        model_mode: props.appConfigs.dime_base_configs.model_mode,
        url_endpoint: props.appConfigs.dime_base_configs.url_endpoint,
        ranking_length: props.appConfigs.dime_base_configs.ranking_length,
        case_sensitive: props.appConfigs.dime_base_configs.case_sensitive,
      },
      validity: {
        data_path: "notset",
        models_path: "notset",
        url_endpoint: "notset",
      },
    };
    this.botURLRef = React.createRef();
    this.dataPathRef = React.createRef();
    this.modelsPathRef = React.createRef();

    this.handleClose = this.handleClose.bind(this);
    this.handleSave = this.handleSave.bind(this);
    this.handleReset = this.handleReset.bind(this);
    this.handleFormElement = this.handleFormElement.bind(this);
    this.handleModelDropDownClick = this.handleModelDropDownClick.bind(this);
    this.handleModelDropDownClose = this.handleModelDropDownClose.bind(this);
    this.handleModelDropDownSetAndClose = this.handleModelDropDownSetAndClose.bind(this);
    this.handleModelsPathChange = this.handleModelsPathChange.bind(this);
  }

  handleClose(event) {
    this.setState({ snackbarIsOpen: false });
  }

  handleFormElement(event, formElement) {
    if (formElement === "case_sensitive") {
      this.setState({
        configs: {
          ...this.state.configs,
          [formElement]: event.target.value === "true" ? true : false
        }
      });
    } else if (formElement === "ranking_length") {
      this.setState({
        configs: {
          ...this.state.configs,
          [formElement]: Math.floor(Number(event.target.value))
        }
      });
    } else {
      this.setState({
        configs: {
          ...this.state.configs,
          [formElement]: event.target.value
        }
      });
    }
  }

  handleModelsPathChange(event) {
    this.props.fetchModels(null, this.state.configs.models_path);
  }

  handleModelDropDownClick(event) {
    this.setState({
      modelDropDownAnchor: event.currentTarget,
      modelDropDownOpen: true,
    })
  }

  handleModelDropDownClose(event) {
    this.setState({
      modelDropDownOpen: false,
      modelDropDownAnchor: null,
    })
  }

  handleModelDropDownSetAndClose(event, element) {
    this.setState({
      configs: {
        ...this.state.configs,
        [element]: event.target.getAttribute("data-model-name")
      },
      modelDropDownOpen: false,
      modelDropDownAnchor: null,
    })
  }

  handleSave(event) {
    console.log("save called");
    this.props.hideAppNotification();
    if (this.state.configs.model_mode === "local") {
      this.setState({
        url_endpoint: this.props.appConfigs.dime_base_configs.url_endpoint,
      })
    } else if (this.state.configs.model_mode === "rest") {
      this.setState({
        models_path: this.props.appConfigs.dime_base_configs.models_path,
        model_name: "Latest",
      })
    }
    let payload = {
      updated_configs: this.state.configs,
    }

    this.setState({
      saveInProgress: true,
      snackbarIsOpen: false,
      validity: {
        data_path: "notset",
        models_path: "notset",
        url_endpoint: "notset",
      }
    });

    axios.post(configs.configEndpoint, payload)
      .then(function (response) {
        console.log(response);
        if (response.data.status !== undefined) {
          if (response.data.status === "valid") {
            // valid configs
            this.setState({
              snackbarMessage: "Configs were successfully persisted!",
              snackbarType: "success",
              snackbarIsOpen: true,
              saveInProgress: false,
              previousConfigs: this.state.configs,
            });
            this.props.fetchConfigs();
          } else if (response.data.status === "invalid") {
            // validate
            this.setState({
              snackbarMessage: "Some configs appears to be invalid!",
              snackbarType: "error",
              snackbarIsOpen: true,
              saveInProgress: false,
              validity: {
                data_path: response.data.metadata.data_path,
                models_path: response.data.metadata.models_path,
                url_endpoint: response.data.metadata.url_endpoint,
              }
            });
          } else {
            // exception
            throw new Error("Unexpected error");
          }

        } else {
          throw new Error("Unexpected response");
        }

      }.bind(this))
      .catch(function (error) {
        console.log(error);
        let notifyTitle = "DIME Configurations Error";
        let notifyBody = "An unknown error occurred while persisting configurations.";
        let snackbarMessage = "An unknown error occurred while persisting configs";
        let snackbarType = "error";

        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          notifyBody = "Failed to retrieve persisting status";
          snackbarMessage = notifyBody;
        } else if (error.request) {
          // The request was made but no response was received
          console.log(error.request);
          notifyBody = "Persisting status was never received";
          snackbarMessage = notifyBody;
        } else {
          // Something happened in setting up the request that triggered an Error
          console.log('Error:', error.message);
          notifyBody = "Failed to send configs for persisting";
          snackbarMessage = notifyBody;
        }
        console.log(error.config);

        this.setState({
          snackbarMessage: snackbarMessage,
          snackbarType: snackbarType,
          snackbarIsOpen: true,
          saveInProgress: false,
        });

        this.props.scrollToTop();
        this.props.showAppNotification(notifyTitle, notifyBody);

      }.bind(this));
  }

  handleReset(event) {
    if (this.state.previousConfigs !== undefined) {
      this.dataPathRef.current.value = this.state.previousConfigs.data_path;
      if (this.state.configs.model_mode === "local") {
        this.modelsPathRef.current.value = this.state.previousConfigs.models_path;
        this.props.fetchModels(null, this.state.previousConfigs.models_path);
      } else if (this.state.configs.model_mode === "rest") {
        this.botURLRef.current.value = this.state.previousConfigs.url_endpoint;
      }

      this.setState({
        validity: {
          data_path: "notset",
          models_path: "notset",
          url_endpoint: "notset",
        },
        configs: {
          ...this.state.previousConfigs,
        },
        snackbarMessage: "All configs were reset",
        snackbarType: "success",
        snackbarIsOpen: true,
      });
      console.log(this.state.configs);
    } else {
      this.setState({
        snackbarMessage: "There are no previous configs to reset",
        snackbarType: "warning",
        snackbarIsOpen: true,
      });
    }
  }

  render() {
    return (
      <>
        <form className="form">
          <Box className="row justify-content-center mb-4">
            <Box className="col-md-5 col-lg-3">
              <label
                htmlFor="basic-url"
                className="form-label white-to-black-ease">Select the Model Mode: <br /><span
                  className="text-muted"> (Local or REST)</span></label>
            </Box>
            <Box className="col-md-7 col-lg-5">
              <Box className="mb-4 mx-0 p-0 w-100" id="modelModeRadioGroup">
                <label
                  className={`list-group-item d-flex gap-2 rubik mx-0 ${this.state.configs.model_mode === "local" ? " container-bg-green" : "container-bg-select"}`}
                  id="modelModeRestLabel">
                  <input
                    className={`form-check-input flex-shrink-0 ${this.state.configs.model_mode === "local" && "material-green"}`}
                    checked={this.state.configs.model_mode === "local" ? true : false}
                    type="radio"
                    name="modelMode"
                    id="modelModeLocal"
                    value="local"
                    onChange={(e) => { this.handleFormElement(e, "model_mode") }} />
                  <span>
                    Local
                    <p className="d-block">Any RASA models trained and stored in the server itself
                    </p>
                  </span>
                </label>
                <label
                  className={`list-group-item d-flex gap-2 rubik mx-0 ${this.state.configs.model_mode === "rest" ? " container-bg-green" : "container-bg-select"}`}
                  id="modelModeRestLabel">
                  <input
                    className={`form-check-input flex-shrink-0 ${this.state.configs.model_mode === "rest" && "material-green"}`}
                    checked={this.state.configs.model_mode === "rest" ? true : false}
                    type="radio"
                    name="modelMode"
                    id="modelModeRest"
                    value="rest"
                    onChange={(e) => { this.handleFormElement(e, "model_mode") }} />
                  <span>
                    Rest
                    <p className="d-block">Any running DIME supported RASA conversational AI in a remote
                      instance
                    </p>
                  </span>
                </label>
              </Box>
            </Box>
          </Box>

          <Box className="row justify-content-center mb-4 model-comman">
            <Box className="col-md-5 col-lg-3">
              <label htmlFor="basic-url" className="form-label white-to-black-ease">Data Path: <br /><span
                className="text-muted">(Path where the RASA data files are at)</span></label>
            </Box>
            <Box className="col-md-7 col-lg-5">
              <Box className="input-group input-group-dark">
                <Box className="input-group input-group-dark">
                  <Box className="d-flex mb-3 p-0 w-100">
                    <span className="input-group-text material-icons">folder</span>
                    <TextField
                      className='w-100'
                      name="dataPath"
                      id="dataPath"
                      hiddenLabel
                      size="small"
                      variant="filled"
                      inputRef={this.dataPathRef}
                      error={this.state.validity.data_path === "invalid" ? true : false}
                      helperText={this.state.validity.data_path === "invalid" ? "Data Path should be a valid data dir" : ""}
                      defaultValue={this.state.configs.data_path}
                      onChange={(e) => { this.handleFormElement(e, "data_path") }} />
                  </Box>
                </Box>
              </Box>
            </Box>
          </Box>

          {this.state.configs.model_mode === "local" &&
            <Box className="row justify-content-center mb-4 model-local">
              <Box className="col-md-5 col-lg-3">
                <label htmlFor="basic-url" className="form-label white-to-black-ease">Models Path: <br /><span
                  className="text-muted">(Path where the RASA models are at)</span></label>
              </Box>
              <Box className="col-md-7 col-lg-5">
                <Box className="input-group input-group-dark">
                  <Box className="d-flex mb-3 p-0 w-100">
                    <span className="input-group-text material-icons">folder</span>
                    <TextField
                      className='w-100'
                      name="modelsPath"
                      id="modelsPath"
                      hiddenLabel
                      size="small"
                      variant="filled"
                      inputRef={this.modelsPathRef}
                      error={this.state.validity.models_path === "invalid" ? true : false}
                      helperText={this.state.validity.models_path === "invalid" ? "Models Path should be a valid models dir" : ""}
                      defaultValue={this.state.configs.models_path}
                      onChange={(e) => { this.handleFormElement(e, "models_path") }}
                      onBlur={(e) => { this.handleModelsPathChange(e) }} />
                  </Box>
                </Box>
              </Box>
            </Box>
          }

          {this.state.configs.model_mode === "local" &&
            <Box className="row justify-content-center mb-4 model-local">
              <Box className="col-md-5 col-lg-3">
                <label htmlFor="basic-url" className="form-label white-to-black-ease">Select a Model: <br /><span
                  className="text-muted"> ("Latest" will automatically pick up the last-trained model)</span></label>
              </Box>
              <Box className="col-md-7 col-lg-5">
                <Box className="input-group input-group-dark">
                  <Box className="d-flex mb-3 p-0 w-100" alignItems={'center'}>
                    <span className="input-group-text material-icons">folder</span>
                    <Button
                      variant="contained"
                      className="form-control overflow-hidden"
                      style={{ justifyContent: "space-between", textTransform: "none", fontSize: '16px' }}
                      fullWidth
                      aria-controls={this.state.modelDropDownOpen ? 'basic-menu' : undefined}
                      aria-haspopup="true"
                      aria-expanded={this.state.modelDropDownOpen ? 'true' : undefined}
                      onClick={(e) => { this.handleModelDropDownClick(e) }}>
                      {this.state.configs.model_name}
                      <KeyboardArrowDown className='float-end' />
                    </Button>
                    <Menu
                      id="basic-menu"
                      className=''
                      open={this.state.modelDropDownOpen}
                      anchorEl={this.state.modelDropDownAnchor}
                      onClose={this.handleModelDropDownClose}
                      MenuListProps={{
                        'aria-labelledby': 'basic-button',
                      }}
                      PaperProps={{
                        style: {
                          maxHeight: 40 * 4.5,
                          minWidth: '15ch',
                          width: '20ch',
                          maxWidth: '37ch'
                        },
                      }}
                    >
                      <MenuItem
                        onClick={(e) => { this.handleModelDropDownSetAndClose(e, 'model_name') }}
                        selected={this.state.configs.model_name === "Latest"}
                        data-model-name={"Latest"}>
                        Latest
                      </MenuItem>
                      {this.props.modelList !== undefined &&
                        this.props.modelList.map((model, idx) => (
                          <MenuItem
                            key={idx}
                            onClick={(e) => { this.handleModelDropDownSetAndClose(e, 'model_name') }}
                            selected={this.state.configs.model_name === model.name}
                            data-model-name={model.name}>
                            {model.name}
                          </MenuItem>
                        ))
                      }
                    </Menu>
                  </Box>
                </Box>
              </Box>
            </Box>
          }

          {this.state.configs.model_mode === "rest" &&
            <Box className="row justify-content-center mb-4 model-local">
              <Box className="col-md-5 col-lg-3">
                <label htmlFor="basic-url" className="form-label white-to-black-ease">Bot URL: <br /><span
                  className="text-muted">(URL for the running RASA bot [protocol://domain:port/])</span></label>
              </Box>
              <Box className="col-md-7 col-lg-5">
                <Box className="input-group input-group-dark">
                  <Box className="d-flex mb-3 p-0 w-100">
                    <span className="input-group-text material-icons">link</span>
                    <TextField
                      className='w-100'
                      name="modelsPath"
                      id="modelsPath"
                      hiddenLabel
                      size="small"
                      variant="filled"
                      inputRef={this.botURLRef}
                      error={this.state.validity.url_endpoint === "invalid" ? true : false}
                      helperText={this.state.validity.url_endpoint === "invalid" ? "Bot URL should be a valid, secure URL" : ""}
                      defaultValue={this.state.configs.url_endpoint}
                      onChange={(e) => { this.handleFormElement(e, "url_endpoint") }} />
                  </Box>
                </Box>
              </Box>
            </Box>
          }

          <Box className="row justify-content-center mb-4 model-local">
            <Box className="col-md-5 col-lg-3">
              <label htmlFor="basic-url" className="form-label white-to-black-ease">Ranking Length: <br /><span
                className="text-muted">(Number of tokens to generate explanations for)</span></label>
            </Box>
            <Box className="col-md-7 col-lg-5">
              <Box className="input-group input-group-dark">
                <Box className="d-flex mb-3 p-0 w-100">
                  <Slider
                    aria-label="Ranking Length"
                    color="info"
                    value={this.state.configs.ranking_length}
                    step={1}
                    marks
                    min={1}
                    max={20}
                    valueLabelDisplay="on"
                    sx={{ height: 6 }}
                    onChange={(e) => { this.handleFormElement(e, "ranking_length") }}
                  />
                </Box>
              </Box>
            </Box>
          </Box>

          <Box className="row justify-content-center mb-4 model-local">
            <Box className="col-md-5 col-lg-3">
              <label htmlFor="basic-url" className="form-label white-to-black-ease">Case Sensitivity: <br /><span
                className="text-muted">(Whether to ignore case or not)</span></label>
            </Box>
            <Box className="col-md-7 col-lg-5">
              <Box className="input-group input-group-dark">
                <Box className="d-flex mb-3 p-0 w-100">
                  <RadioGroup
                    row
                    aria-labelledby="demo-controlled-radio-buttons-group"
                    name="controlled-radio-buttons-group"
                    value={this.state.configs.case_sensitive}
                    onChange={(e) => { this.handleFormElement(e, "case_sensitive") }}
                  >
                    <FormControlLabel value={true} control={<Radio color='info' />} label="Consider Case" />
                    <FormControlLabel value={false} control={<Radio color='info' />} label="Ignore Case" />
                  </RadioGroup>
                </Box>
              </Box>
            </Box>
          </Box>

          <Box className="row mb-4 model-common justify-content-center">
            <Box className="col-md-12 col-lg-8">
              {this.state.saveInProgress ?
                <Stack direction="row" spacing={1} className={"float-end"}>
                  <LoadingButton
                    loading
                    loadingPosition="start"
                    startIcon={<Save />}
                    variant="outlined"
                    className="float-end explanation-loading-button"
                    size="1.5rem"
                    sx={{ height: "2.4rem" }}
                    disabled>
                    Save
                  </LoadingButton>
                  <Button variant='outlined' className="float-end app-button"
                    sx={{ border: "none", '&:hover': { border: "none" } }} startIcon={<RestartAlt />}
                    disabled>
                    Reset
                  </Button>
                </Stack>
                :
                <Stack direction="row" spacing={1} className={"float-end"}>
                  <Button variant='outlined' className="float-end app-button app-button-steel"
                    sx={{ border: "none", '&:hover': { border: "none" } }} startIcon={<Save />}
                    onClick={this.handleSave}>
                    Save
                  </Button>
                  <Button variant='outlined' className="float-end app-button app-button-red"
                    sx={{ border: "none", '&:hover': { border: "none" } }} startIcon={<RestartAlt />}
                    onClick={this.handleReset}>
                    Reset
                  </Button>
                </Stack>
              }
            </Box>
          </Box>
        </form>

        <Snackbar
          open={this.state.snackbarIsOpen}
          autoHideDuration={3000}
          onClose={this.handleClose}
          anchorOrigin={{ vertical: `${configs.snackbarVerticalPosition}`, horizontal: `${configs.snackbarHorizontalPostion}` }}>
          <Alert
            onClose={this.handleClose}
            severity={this.state.snackbarType}
            sx={{ width: '100%' }}>
            {this.state.snackbarMessage.toString()}
          </Alert>
        </Snackbar>
      </>
    );
  }
}
