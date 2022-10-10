import React, { Component } from "react";
import {
  Box,
  Stack,
  Alert,
  AlertTitle,
  Stepper,
  Step,
  StepLabel,
  Typography,
  StepContent,
  Button,
  Paper,
} from "@mui/material";
import { configs } from "../../configs";

export default class OffCanvasInstructions extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeStepperStep: 0,
      steps: [
        {
          label: "Configure",
          description: `Configurations let you change the directory paths for training data, 
            models, select latest model or specify the URL for a running RASA model, ranking length, 
            and case-sensitivity. If you did not configure the dime_configs.yml before running DIME 
            server, you still can change these in the Config tab. ⚙️`,
        },
        {
          label: "Explain",
          description: `Input the sentence you want explanations for in the Explanations tab and and click on 
            Explain. You can Abort your request at anytime! ❌`,
        },
        {
          label: "Visualize",
          description: `Visualizations are automatically shown after Explanations request, however, you 
          can see the all the previously generated explanations in the Explanations page. Notice that you 
          also can upload Explanations to the server. You can use 'PEAK' to quickly visualize portable 
          explanation files without uploading them. ⚡`,
        },
      ],
    };

    this.handleNext = this.handleNext.bind(this);
    this.handleBack = this.handleBack.bind(this);
    this.handleReset = this.handleReset.bind(this);
  }

  handleNext(event) {
    this.setState({ activeStepperStep: this.state.activeStepperStep + 1 });
  }

  handleBack(event) {
    this.setState({ activeStepperStep: this.state.activeStepperStep - 1 });
  }

  handleReset(event) {
    this.setState({ activeStepperStep: 0 });
  }

  render() {
    return (
      <Box
        className="offcanvas offcanvas-end container-bg-custom material-matt-black rounded-0 quick-instructions-offcanvas"
        data-bs-scroll="true"
        tabIndex="-1"
        id="dime-instructions-canvas"
        aria-labelledby="offcanvasWithBothOptionsLabel"
      >
        <Box className="offcanvas-header">
          <h5 className="offcanvas-title" id="offcanvasWithBothOptionsLabel">
            Quick Instructions
          </h5>
          <button
            type="button"
            className="btn-close btn-close-white"
            data-bs-dismiss="offcanvas"
            aria-label="Close"
          ></button>
        </Box>
        <Box className="offcanvas-body scroll-hidden">
          <Stack spacing={2} direction={"column"}>
            <Box sx={{ maxWidth: 400, color: "white" }}>
              <Stepper
                activeStep={this.state.activeStepperStep}
                orientation="vertical"
              >
                {this.state.steps.map((step, index) => (
                  <Step key={step.label} sx={{ color: "white" }}>
                    <StepLabel
                      optional={
                        index === 2 ? (
                          <Typography variant="caption" color={"white"}>
                            Last step
                          </Typography>
                        ) : null
                      }
                    >
                      {step.label}
                    </StepLabel>
                    <StepContent>
                      <Typography>{step.description}</Typography>
                      <Box sx={{ mb: 2 }}>
                        <div>
                          <Button
                            variant="contained"
                            color={"info"}
                            onClick={this.handleNext}
                            sx={{ mt: 1, mr: 1 }}
                          >
                            {index === this.state.steps.length - 1
                              ? "Done"
                              : "Continue"}
                          </Button>
                          <Button
                            disabled={index === 0}
                            color={"info"}
                            onClick={this.handleBack}
                            sx={{ mt: 1, mr: 1 }}
                          >
                            Back
                          </Button>
                        </div>
                      </Box>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
              {this.state.activeStepperStep === this.state.steps.length && (
                <Paper
                  className="material-matt-black"
                  square
                  elevation={0}
                  sx={{ p: 3, borderRadius: 1 }}
                >
                  <Typography color={"white"}>Cheers! 🥳</Typography>
                  <Button
                    className="app-button-pink"
                    onClick={this.handleReset}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    Reset
                  </Button>
                </Paper>
              )}
            </Box>
            <Alert severity="info">
              <AlertTitle>
                What is <strong>DIME</strong> and <strong>Dual Score</strong>?
              </AlertTitle>
              <strong>DIME</strong> stands for Dual Interpretable Model-agnostic
              Explanations; which enables explainability for mainly text
              classification models.
              <p />
              <p>
                In this implementation, DIME can be used to explain{" "}
                <strong>RASA DIET</strong> classifiers.
                <strong>Dual Score</strong> indicates the local explanations of
                the tokens filtered based on their global feature importance
              </p>
              <p>
                i.e. DIME visualizes the importance of the individual
                words/tokens in a given sentence and indicates how important
                each token is towards the predicted intent. However, dual
                visualizations includes only the tokens with a non-zero global
                feature importance.{" "}
              </p>
            </Alert>
            <Alert severity="info">
              <AlertTitle>Plug-and-play Dual Explanations</AlertTitle>
              <strong>Dual Explanations</strong> are simply the results
              generated by DIME. Since generating Dual Explanations is time
              consuming, the explanations have been made exportable as JSON
              files which can be visualized instantly at any time. Which means
              you are able to generate explanations only once, visualize it
              lightning fast, at anytime, on any machine that has DIME
              installed.
            </Alert>
            <Alert severity="info">
              <AlertTitle>RASA Version and Supported Models</AlertTitle>
              DIME version <strong>1.x.x</strong> fully supports RASA version
              <strong>2.2.8</strong> up to
              <strong>2.8.8</strong>. Find the compatibility matrix{" "}
              <a
                href={`${configs.dimeDocsMatrix}`}
                target="_blank"
                rel="noreferrer"
              >
                here
              </a>
            </Alert>
            <Alert severity="error">
              <AlertTitle>DIET Compatibility</AlertTitle>
              Note that not all DIET classifiers are compatible with DIME. In
              order to use DIME, you need a DIME-compatible DIET classifier.
              Refer the{" "}
              <a
                href={`${configs.dimeDocsDIET}`}
                target="_blank"
                rel="noreferrer"
              >
                docs
              </a>{" "}
              to see how to attach a DIME-compatible DIET classifier to your
              RASA Pipeline.
            </Alert>
          </Stack>
        </Box>
      </Box>
    );
  }
}
