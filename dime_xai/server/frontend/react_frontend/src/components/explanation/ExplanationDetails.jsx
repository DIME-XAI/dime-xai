import React, { Component } from 'react';
import { Alert, Box, Collapse, IconButton, Typography } from '@mui/material';
import { Close } from '@mui/icons-material';
import { configs } from '../../configs';

export default class ExplanationDetails extends Component {
  constructor(props) {
    super(props);
    this.state = {
      setOpen: true
    }
  }

  render() {
    return (
      <Box className="mb-5">
        <Box sx={{ width: '100%' }}>
          <Collapse in={this.state.setOpen}>
            <Alert
              action={
                <IconButton
                  aria-label="close"
                  color="inherit"
                  size="small"
                  onClick={() => {
                    this.setState({ setOpen: false });
                  }}
                >
                  <Close fontSize="inherit" />
                </IconButton>
              }
              sx={{ mb: 2 }}
              severity="info"
              color="info"
              className='app-info-box'>
              Learn how to interpret Dual Feature Importance Scores <a href={`${configs.dimeDocsHost}`} target={'_blank'} rel={'noreferrer'}>here</a>
            </Alert>
          </Collapse>
        </Box>

        <Typography className="css-1g8t8rh" variant="h5" gutterBottom component="div" sx={{ fontWeight: 'medium' }} >Summary</Typography>
        <table className="table table-sm container-middle container-bg">
          <tbody>
            <tr>
              <td>Instance</td>
              <td>{this.props.data.dual[0].instance}</td>
            </tr>
            <tr>
              <td>Case</td>
              <td>{this.props.data.config.case_sensitive ? "On" : "Off"}</td>
            </tr>
            <tr>
              <td>Ranking Length</td>
              <td>{this.props.data.config.ranking_length}</td>
            </tr>
          </tbody>
        </table>
      </Box>
    );
  }
}
