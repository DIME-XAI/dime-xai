import React, { Component } from 'react';
import axios, { CanceledError } from 'axios';
import { v4 as uuidv4 } from 'uuid';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import { Box, Button, Stack, TextField, ToggleButton } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { RestartAlt, MarkChatRead, Cancel, Keyboard, Save } from '@mui/icons-material'
import ExplanationDetails from '../explanation/ExplanationDetails';
import GlobalExplanation from '../explanation/GlobalExplanation';
import DualExplanation from '../explanation/DualExplanation';
import { configs } from '../../configs';


const Alert = React.forwardRef((props, ref) =>
  <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />
);

export default class ExplanationsTab extends Component {
  constructor(props) {
    super(props);
    this.state = {
      dataInstanceValue: props.appConfigs.dime_base_configs.data_instance,
      previousDataInstanceValue: props.appConfigs.dime_base_configs.data_instance,
      dataInstanceHelperText: "Invalid Data Instance",
      dataInstanceValidity: "notset",
      explainButtonInProgress: false,
      explanation: undefined,
      explanationRequestId: undefined,
      snackbarIsOpen: false,
      snackbarMessage: '',
      snackbarType: "success",
      language: "EN",
      keyboardEnabled: props.appConfigs.custom_configs.keyboard_enabled,
    };

    this.dataInstanceRef = React.createRef();
    this.cancelTokenExplainRequest = React.createRef();

    // button handlers
    this.handleExplain = this.handleExplain.bind(this);
    this.handleReset = this.handleReset.bind(this);
    this.handleSnackbarClose = this.handleSnackbarClose.bind(this);
    this.handleAbort = this.handleAbort.bind(this);

    // keyboard interface handlers
    this.handleMessageKeyPress = this.handleMessageKeyPress.bind(this);
    this.handleMessageKeyDown = this.handleMessageKeyDown.bind(this);
    this.handleMessageKeyUp = this.handleMessageKeyUp.bind(this);
    this.convertToSinhala = this.convertToSinhala.bind(this);

    // keyboard state refs
    this.previous_input_text = ""
    this.new_input_text = ""
    this.outofscope_text = ""
  }

  handleMessageKeyPress(event) {
    console.log("key-p");
    let key = (event.keyCode ? event.keyCode : event.which);
    if (this.state.language === "SI") {
      if (key >= 20 && key <= 126) {
        this.previous_input_text = this.previous_input_text + String.fromCharCode(key);
      }
      console.log("Accumilated: " + this.previous_input_text);
    }
  }

  handleMessageKeyDown(event) {
    console.log("key-d");

    // Only activates if the language is Sinhala
    let key = (event.keyCode ? event.keyCode : event.which);

    // Handling the Backspace for Sinhalese
    if (this.state.language === "SI") {
      if (key === 8) {
        let selection = window.getSelection();
        let selectedText = selection.toString();

        if (!selectedText) {
          this.previous_input_text = "";
          let current_val = this.dataInstanceRef.current.value;
          current_val = current_val.substring(current_val.length - 1, -1);
          this.outofscope_text = current_val;
        } else {
          this.previous_input_text = "";
          let current_val = this.dataInstanceRef.current.value;
          let textComponent = document.getElementsByClassName('rw-new-message')[0];

          let startPos = textComponent.selectionStart;
          let endPos = textComponent.selectionEnd;
          // let selectedText = textComponent.value.substring(startPos, endPos);

          // console.log(startPos, endPos, selectedText);
          this.outofscope_text = current_val.substring(0, startPos) + current_val.substring(endPos,);
        }
      }
    }

    // // Handling Enter (Submitting Text when Enter is pressed)
    // if (key === 13) {
    //     $(kbi_init_props["sendMessageElement"]).trigger("click");
    // }
    console.log(this.new_input_text);
  }

  handleMessageKeyUp(event) {
    console.log("key-u");

    // Only activates if the language is Sinhala
    if (this.state.language === "SI") {
      this.new_input_text = this.convertToSinhala(this.previous_input_text);
      console.log(this.new_input_text);
      this.dataInstanceRef.current.value = this.outofscope_text + this.new_input_text;
    }

  }

  convertToSinhala(text) {
    // Vowel Keys and Maps
    let sinhala_vowels_keys = [
      'uu', 'oo', 'oe', 'aa', 'AA', 'Aa', 'ae', 'ii', 'ie', 'ee', 'ea', 'ei', 'uu', 'au',
      'O', 'a', 'A', 'i', 'e', 'u', 'U', 'o', 'E', 'I'
    ];
    let sinhala_vowel_pure_map = {
      'uu': 'ඌ', 'oo': 'ඕ', 'oe': 'ඕ', 'aa': 'ආ', 'AA': 'ඈ', 'Aa': 'ඈ', 'ae': 'ඈ', 'ii': 'ඊ', 'ie': 'ඊ', 'ee': 'ඒ', 'ea': 'ඒ', 'ei': 'ඒ', 'au': 'ඖ',
      'O': 'ඖ', 'a': 'අ', 'A': 'ඇ', 'i': 'ඉ', 'e': 'එ', 'u': 'උ', 'U': 'උ', 'o': 'ඔ', 'E': 'ඓ', 'I': 'ඓ'
    };
    let sinhala_vowel_suffix_map = {
      'uu': 'ූ', 'oo': 'ෝ', 'oe': 'ෝ', 'aa': 'ා', 'AA': 'ෑ', 'Aa': 'ෑ', 'ae': 'ෑ', 'ii': 'ී', 'ie': 'ී', 'ee': 'ේ', 'ea': 'ේ', 'ei': 'ේ', 'au': 'ෞ',
      'O': 'ෞ', 'a': '', 'A': 'ැ', 'i': 'ි', 'e': 'ෙ', 'u': 'ු', 'o': 'ො', 'E': 'ෛ', 'I': 'ෛ'
    };

    // Non-joining Character Keys and Maps [ + '\u200D']
    let sinhala_nonjoining_keys = [
      'RR', 'z', 'x', 'H', 'R'
    ];
    let sinhala_nonjoining_map = {
      'RR': 'ඎ',
      'z': 'ර්\u200D',
      'x': 'ං',
      'H': 'ඃ',
      'R': 'ඍ'
    };

    // Consonent Keys and Maps
    let sinhala_consonent_keys = [
      'nndh', 'nnd', 'nng', 'mmb',
      'GN', 'KN', 'Lu', 'Th', 'Dh', 'gh', 'Ch', 'ph', 'kh', 'bh',
      'Sh', 'sh', 'dh', 'ch', 'th',
      'N', 'L', 'K', 'G', 'T', 'D', 'P', 'B', 'C', 'X', 'J',
      't', 'k', 'd', 'n', 'p', 'b', 'm', 'M', 'Y', 'y', 'j', 'l', 'v', 'w', 'V', 'W',
      's', 'S', 'h', 'f', 'F', 'g', 'c',
      'r'
    ];
    let sinhala_consonant_map = {
      'nndh': 'ඳ', 'nnd': 'ඬ', 'nng': 'ඟ', 'mmb': 'ඹ',
      'GN': 'ඥ', 'KN': 'ඤ', 'Lu': 'ළු', 'Th': 'ථ', 'Dh': 'ධ', 'gh': 'ඝ', 'Ch': 'ඡ', 'ph': 'ඵ', 'kh': 'ඛ', 'bh': 'භ',
      'Sh': 'ෂ', 'sh': 'ශ', 'dh': 'ද', 'ch': 'ච', 'th': 'ත',
      'N': 'ණ', 'L': 'ළ', 'K': 'ඛ', 'G': 'ඝ', 'T': 'ඨ', 'D': 'ඪ', 'P': 'ඵ', 'B': 'භ', 'C': 'ඡ', 'X': 'ඞ', 'J': 'ඣ',
      't': 'ට', 'k': 'ක', 'd': 'ඩ', 'n': 'න', 'p': 'ප', 'b': 'බ', 'm': 'ම', 'M': 'ම', 'Y': 'ය', 'y': 'ය', 'j': 'ජ', 'l': 'ල', 'v': 'ව', 'w': 'ව', 'V': 'ව', 'W': 'ව',
      's': 'ස', 'S': 'ස', 'h': 'හ', 'f': 'ෆ', 'F': 'ෆ', 'g': 'ග', 'c': 'ච',
      'r': 'ර'
    };
    // consonantsUni[14] = 'ළු'; consonants[14] = 'Lu'; TODO HANDLE THIS SPC

    // Special Character Keys and Maps
    let sinhala_special_keys = [
      'ruu',
      'ru'
    ];
    let sinhala_special_map = {
      'ruu': 'ෲ',
      'ru': 'ෘ'
    };

    let EN_pattern, SI_pattern, RegEx_pattern;

    // Replacing non-joining characters
    sinhala_nonjoining_keys.forEach((nj_char, idx) => {
      EN_pattern = nj_char;
      SI_pattern = sinhala_nonjoining_map[nj_char];
      RegEx_pattern = new RegExp(EN_pattern, "g");
      text = text.replace(RegEx_pattern, SI_pattern);
    });

    // Replacing special consonents
    sinhala_special_keys.forEach((sp_char, idx) => {
      sinhala_consonent_keys.forEach((con_char, idx) => {
        EN_pattern = con_char + sp_char;
        SI_pattern = sinhala_consonant_map[con_char] + sinhala_special_map[sp_char];
        RegEx_pattern = new RegExp(EN_pattern, "g");
        text = text.replace(RegEx_pattern, SI_pattern);
      });
    });

    // Replacing consonants + Rakaransha + vowel modifiers
    sinhala_consonent_keys.forEach((con_char, idx) => {
      sinhala_vowels_keys.forEach((v_char, idx) => {
        EN_pattern = con_char + "r" + v_char;
        SI_pattern = sinhala_consonant_map[con_char] + "්‍ර" + sinhala_vowel_suffix_map[v_char];
        RegEx_pattern = new RegExp(EN_pattern, "g");
        text = text.replace(RegEx_pattern, SI_pattern);
      });
      EN_pattern = con_char + "r";
      SI_pattern = sinhala_consonant_map[con_char] + "්‍ර";
      RegEx_pattern = new RegExp(EN_pattern, "g");
      text = text.replace(RegEx_pattern, SI_pattern);
    });

    // Replacing consonents + vowel modifiers
    sinhala_consonent_keys.forEach((con_char, idx) => {
      sinhala_vowels_keys.forEach((v_char, idx) => {
        EN_pattern = con_char + v_char;
        SI_pattern = sinhala_consonant_map[con_char] + sinhala_vowel_suffix_map[v_char];
        RegEx_pattern = new RegExp(EN_pattern, "g");
        text = text.replace(RegEx_pattern, SI_pattern);
      });
    });

    // Replacing consonents + HAL
    sinhala_consonent_keys.forEach((con_char, idx) => {
      EN_pattern = con_char;
      SI_pattern = sinhala_consonant_map[con_char] + "්";
      RegEx_pattern = new RegExp(EN_pattern, "g");
      text = text.replace(RegEx_pattern, SI_pattern);
    });

    // Replacing vowels
    sinhala_vowels_keys.forEach((v_char, idx) => {
      EN_pattern = v_char;
      SI_pattern = sinhala_vowel_pure_map[v_char];
      RegEx_pattern = new RegExp(EN_pattern, "g");
      text = text.replace(RegEx_pattern, SI_pattern);
    });

    console.log(text);
    return (text);
  }

  handleSnackbarClose(event) {
    this.setState({ snackbarIsOpen: false });
  }

  validateDataInstance(dataInstance) {
    if (dataInstance.toString().trim() === "") {
      this.setState({
        snackbarMessage: "Invalid Data Instance",
        snackbarType: "error",
        snackbarIsOpen: true,
        dataInstanceValidity: "invalid",
        dataInstanceHelperText: "Data Instance must be longer than 1 Token",
      });
      return false;
    } else if (dataInstance.toString().trim().split(" ").length < 2) {
      this.setState({
        snackbarMessage: "Invalid Data Instance",
        snackbarType: "warning",
        snackbarIsOpen: true,
        dataInstanceValidity: "invalid",
        dataInstanceHelperText: "Data Instances shorter than 2 Tokens are less Interpretable",
      });
      return false;
    }

    return true;
  }

  handleExplain(event) {
    this.props.hideAppNotification();

    // validate
    if (!this.validateDataInstance(this.dataInstanceRef.current.value)) {
      return;
    }

    let request_id = uuidv4();
    let payload = {
      data_instance: this.dataInstanceRef.current.value,
      request_id: request_id,
      app_env: this.props.appConfigs.custom_configs.app_env,
      model_type: this.props.appConfigs.dime_base_configs.model_type,
      headers: { 'Content-Type': 'application/json' }
    }

    console.log("payload", payload);

    this.setState({
      explainButtonInProgress: true,
      explanation: undefined,
      snackbarIsOpen: false,
      explanationRequestId: request_id,
      dataInstanceValidity: "notset",
    });

    this.cancelTokenExplainRequest.current = axios.CancelToken.source();

    console.log("[request id] " + request_id);

    axios.post(configs.explainEndpoint, payload, { cancelToken: this.cancelTokenExplainRequest.current.token })
      .then(function (response) {
        console.log(response);
        if (response.data.status !== undefined) {
          if (response.data.status === "success") {
            let explanation = JSON.parse(response.data.explanation);
            this.setState({
              snackbarMessage: "Explanation generated successfully!",
              snackbarType: "success",
              snackbarIsOpen: true,
              explanation: explanation,
              explainButtonInProgress: false,
            });
            this.props.fetchStats();

          } else {
            throw new Error("Unexpected error");
          }

        } else {
          throw new Error("Unexpected response");
        }

      }.bind(this))
      .catch(function (error) {
        console.log(error);
        let notifyTitle = "DIME Explanation Error";
        let notifyBody = "An unknown error occurred while generating the explanation. Please try again a bit later.";
        let snackbarMessage = "An unknown error occurred while requesting the explanation";
        let snackbarType = "error";

        if (error instanceof CanceledError) {
          notifyBody = "Explanation Request Aborted!";
          snackbarMessage = notifyBody;
          snackbarType = "warning";
        } else if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          notifyBody = "Failed to obtain a valid explanation";
          snackbarMessage = notifyBody;
        } else if (error.request) {
          // The request was made but no response was received
          console.log(error.request);
          notifyBody = "Explanation was never received";
          snackbarMessage = notifyBody;
        } else {
          // Something happened in setting up the request that triggered an Error
          console.log('Error:', error.message);
          notifyBody = "Failed to request the explanation";
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
  }

  handleReset(event) {
    this.dataInstanceRef.current.value = this.state.previousDataInstanceValue;
    this.setState({
      explanation: undefined,
      dataInstanceValidity: "notset",
    });
  }

  handleAbort(event) {
    let payload = {
      request_id: this.state.explanationRequestId,
      headers: {
        'Content-Type': 'application/json'
      }
    }
    console.log("[abort request id] " + payload.request_id);
    axios.post(configs.abortExplainEndpoint, payload)
      .then(function (response) {
        console.log(response);
        if (response.data.status !== undefined) {
          if (response.data.status === "success") {
            this.setState({
              explainButtonInProgress: false,
              explanationRequestId: undefined,
            });

            this.cancelTokenExplainRequest.current.cancel();
            console.log('request aborted!');

          } else {
            throw new Error("Abort request was discarded");
          }

        } else {
          throw new Error("Failed to send abort request");
        }

      }.bind(this))
      .catch(function (error) {
        console.log(error);
        this.setState({
          snackbarMessage: "Request aborting failed",
          snackbarType: "error",
          snackbarIsOpen: true,
          explainButtonInProgress: false,
        });
      }.bind(this));
  }

  render() {
    return (
      <>
        <Box className="tab-pane fade show active" id="exp-tab-pane" role="tabpanel" aria-labelledby="exp-tab"
          tabIndex="0">
          <Box className="row p-3 pb-0 justify-content-center">
            <Box className="alert app-alert mb-4" role="alert">
              <p className="white-to-black-ease">Provide a sentence to be explained and make sure it is longer than
                a
                single word. Then, simply tap <kbd className="fs-6 kbd material-matt-black">Explain</kbd> button to
                get
                the explanation. If
                required to
                change the current DIME configurations, plese navigate to the <kbd
                  className="fs-6 kbd material-matt-black app-cursor-pointer" onClick={this.props.handleConfigTab}>Configurations</kbd> tab.
              </p>
            </Box>
            <Box sx={{ marginTop: 3 }}>
              <Box className="row justify-content-center mb-4 mt-4 model-comman" >
                <Box className="col-md-5 col-lg-3">
                  <label htmlFor="basic-url" className="form-label white-to-black-ease">Data Instance: <br /><span
                    className="text-muted">(Sentence to be explained)</span></label>
                </Box>
                <Box className="col-md-7 col-lg-5">
                  <Box className="input-group input-group-dark">
                    <Box className="d-flex mb-3 p-0 w-100">
                      <span className="input-group-text material-icons" id="dataInstanceSpan">chat</span>
                      <TextField
                        className='w-100'
                        id="dataInstance"
                        hiddenLabel
                        size="small"
                        variant="filled"
                        inputRef={this.dataInstanceRef}
                        defaultValue={this.state.dataInstanceValue}
                        error={this.state.dataInstanceValidity === "invalid"}
                        helperText={this.state.dataInstanceValidity === "invalid" ? this.state.dataInstanceHelperText : ""}
                        onKeyPress={(e) => { this.handleMessageKeyPress(e) }}
                        onKeyDown={(e) => { this.handleMessageKeyDown(e) }}
                        onKeyUp={(e) => { this.handleMessageKeyUp(e) }} />
                    </Box>
                  </Box>
                </Box>
                <Box className="col-md-12 col-lg-8">
                  {this.state.keyboardEnabled &&
                    <ToggleButton
                      sx={{ width: "80px", '&.MuiToggleButton-root': { color: "black" } }}
                      value="check"
                      selected={this.state.language === "EN"}
                      onChange={() => {
                        let lang = undefined;
                        this.state.language === "EN" ? lang = "SI" : lang = "EN";
                        this.setState({ language: lang })
                      }}>
                      <Keyboard sx={{ marginRight: "4px" }} />
                      {this.state.language === "EN" ? "EN" : "SI"}
                    </ToggleButton>
                  }
                  {this.state.explainButtonInProgress ?
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
                        Explain
                      </LoadingButton>
                      {this.props.appConfigs.custom_configs.app_env === "strict_local" ?
                        <Button variant='outlined' className="float-end app-button"
                          sx={{ border: "none", '&:hover': { border: "none" } }} startIcon={<RestartAlt />}
                          disabled>
                          Reset
                        </Button>
                        :
                        <Button variant='outlined' className="float-end app-button app-button-red ms-2"
                          sx={{ border: "none", '&:hover': { border: "none" } }} startIcon={<Cancel />}
                          onClick={this.handleAbort}>
                          Abort
                        </Button>
                      }
                    </Stack>
                    :
                    <Stack direction="row" spacing={1} className={"float-end"}>
                      <Button variant='outlined' className="float-end app-button app-button-steel"
                        sx={{ border: "none", '&:hover': { border: "none" } }} startIcon={<MarkChatRead />}
                        onClick={this.handleExplain}>
                        Explain
                      </Button>
                      <Button variant='outlined' className="float-end app-button app-button-red"
                        sx={{ border: "none", '&:hover': { border: "none" } }} startIcon={<RestartAlt />}
                        onClick={this.handleReset}>
                        Reset
                      </Button>
                    </Stack>
                  }
                </Box>
                {this.state.explanation === undefined ?
                  <Box></Box>
                  :
                  <Box className="row mt-4 pt-4 mb-0 model-common justify-content-center">
                    <Box className="col-12 col-lg-8">
                      <ExplanationDetails data={this.state.explanation} />
                      <GlobalExplanation color="purple" data={this.state.explanation} />
                      <DualExplanation color="green" data={this.state.explanation} />
                    </Box>
                  </Box>
                }
              </Box>
            </Box>
          </Box>
        </Box>
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
