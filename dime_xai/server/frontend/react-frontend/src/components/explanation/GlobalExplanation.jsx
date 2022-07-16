import React from 'react';
import ExplanationBar from './ExplanationBar';
import { Accordion, AccordionDetails, AccordionSummary, Box, Typography } from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import TwoColDataTable from '../dataTable/TwoColDataTable';

class GlobalExplanation extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      explanationTitle: `Explanation for "${this.props.data.dual[0].instance}"`,
      color: this.props.color,
      data: this.props.data,
    };
  }

  render() {
    let globalScores = Object.keys(this.state.data.dual[0].global.probability_scores).map((key, index) =>
      <ExplanationBar
        key={key}
        sliderValue={Number((Number(this.state.data.dual[0].global.probability_scores[key]) * 100).toFixed(2)).toString() + "%"}
        token={key.toString()}
        color={this.state.color} />
    );
    let allFeatures = Object.keys(this.props.data.dual[0].global.probability_scores);
    let selectedFeatures = Object.keys(this.props.data.dual[0].global.feature_selection);
    let ignoredFeatures = {};

    if (allFeatures.length - selectedFeatures.length > 0) {
      allFeatures.forEach((token, idx) => {
        if (!selectedFeatures.includes(token)) {
          ignoredFeatures[token] = token;
        }
      });
    } else {
      ignoredFeatures = {};
    }
    let featureData = {
      "Tokens Selected": selectedFeatures.length > 0 ? selectedFeatures.join(", ") : "None",
      "Tokens Ignored": (allFeatures.length - selectedFeatures.length) > 0 ? Object.keys(ignoredFeatures).join(", ") : "None"
    }

    return (
      <Box className="mb-5">
        <Typography
          variant="h6"
          gutterBottom
          component="div"
          sx={{ fontWeight: 'medium' }} >
          Global Feature Importance
        </Typography>
        <Box className="mb-4">
          <table className="table table-sm container-middle container-bg">
            <tbody>
              <tr>
                <td># of Selected Features</td>
                <td>{selectedFeatures.length}</td>
              </tr>
              <tr>
                <td># of Ignored Features</td>
                <td>{allFeatures.length - selectedFeatures.length}</td>
              </tr>
            </tbody>
          </table>
        </Box>
        <Box className="mb-4">
          {globalScores}
        </Box>
        <Box className="mb-5">
          <Accordion className="explanation-accordian explanation-accordian-global">
            <AccordionSummary
              expandIcon={<ExpandMore />}
              aria-controls="panel1a-content"
              id="panel1a-header">
              <Typography>Raw Global Feature Imporance Scores</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TwoColDataTable
                data={this.props.data.dual[0].global.feature_importance}
                classNames="app-table-global" />
            </AccordionDetails>
          </Accordion>
          <Accordion className="explanation-accordian explanation-accordian-global">
            <AccordionSummary
              expandIcon={<ExpandMore />}
              aria-controls="panel2a-content"
              id="panel2a-header"
            >
              <Typography>Feature Selection</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TwoColDataTable
                data={featureData}
                classNames="app-table-global" />
            </AccordionDetails>
          </Accordion>
        </Box>
      </Box>
    );
  }
}

export default GlobalExplanation;