import { Box } from "@mui/material";
import React, { Component } from "react";
import AppTile from "./AppTile";

export default class ModelsPageBanner extends Component {
  constructor(props) {
    super(props);
    this.state = {
      explanationsListState: false,
    };

    this.showExplanationList = this.showExplanationList.bind(this);
  }

  showExplanationList(state) {
    this.setState({ explanationsListState: state });
  }

  render() {
    return (
      <>
        <Box
          className="row row-cols-1 row-cols-lg-1"
          sx={{ marginY: 2, marginBottom: 3 }}
        >
          <AppTile
            bgcolor=""
            align="justify-content-start"
            margin="me-0 me-lg-0"
            icon="psychology_alt"
            iconColor="material-steel-f"
            count=""
            title="Dual Explanations"
            content="All dual explanations previously generated can be visualized here, lightning fast. Have you tried Peak? It's even faster."
            button={{
              button: false,
            }}
            customButton=""
          />
        </Box>
      </>
    );
  }
}
