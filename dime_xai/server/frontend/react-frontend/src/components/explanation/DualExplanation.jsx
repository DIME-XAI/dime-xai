import React from "react";
import ExplanationBar from "./ExplanationBar";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Typography,
} from "@mui/material";
import { ExpandMore } from "@mui/icons-material";
import TwoColDataTable from "../dataTable/TwoColDataTable";

class DualExplanation extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      explanationTitle: `Explanation for "${this.props.data.dual[0].instance}"`,
      color: this.props.color,
      data: this.props.data,
    };
  }

  render() {
    let dualScores = Object.keys(
      this.state.data.dual[0].dual.probability_scores
    ).map((key, index) => (
      <ExplanationBar
        key={key}
        sliderValue={
          Number(
            (
              Number(this.state.data.dual[0].dual.probability_scores[key]) * 100
            ).toFixed(2)
          ).toString() + "%"
        }
        token={key.toString()}
        color={this.state.color}
      />
    ));
    return (
      <Box className="mb-5">
        <Typography
          variant="h6"
          gutterBottom
          component="div"
          sx={{ fontWeight: "medium" }}
        >
          Dual Feature Importance
        </Typography>
        <Box className="mb-4">
          <table className="table table-sm container-middle container-bg">
            <tbody>
              <tr>
                <td>Instance</td>
                <td>{this.props.data.dual[0].instance}</td>
              </tr>
              <tr>
                <td>Predicted Intent</td>
                <td>
                  <kbd className="fs-6 kbd material-orange">
                    {this.props.data.dual[0].global.predicted_intent}
                  </kbd>
                </td>
              </tr>
              <tr>
                <td>Predicted DIET Confidene</td>
                <td>{this.props.data.dual[0].global.predicted_confidence}</td>
              </tr>
            </tbody>
          </table>
        </Box>
        <Box className="mb-4">{dualScores}</Box>
        <Box className="">
          <Accordion className="explanation-accordian explanation-accordian-dual">
            <AccordionSummary
              expandIcon={<ExpandMore />}
              aria-controls="panel1a-content"
              id="panel1a-header"
            >
              <Typography>Raw Dual Feature Importance Scores</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TwoColDataTable
                data={this.props.data.dual[0].dual.feature_importance}
                classNames="app-table-dual"
              />
            </AccordionDetails>
          </Accordion>
        </Box>
      </Box>
    );
  }
}

export default DualExplanation;
