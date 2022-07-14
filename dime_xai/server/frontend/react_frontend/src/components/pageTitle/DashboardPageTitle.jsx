import React, { Component } from 'react';
import { Button } from '@mui/material';
import { Article } from '@mui/icons-material';

export default class DashboardPageTitle extends Component {
  render() {
    return (
      <div className="row mb-1">
        <div className="col w-100 mx-0 px-0 justify-content-between d-inline-block">
          <h4 className="float-start h-100 mt-1 dime-page-title"><strong>DIME</strong></h4>
          <Button variant="outlined" startIcon={<Article />}
            sx={{ border: "none", '&:hover': { border: "none" } }}
            className="float-end app-button app-button-blue mb-md-0 mb-sm-0 mx-2"
            data-bs-toggle="offcanvas" data-bs-target="#dime-instructions-canvas"
            aria-controls="offcanvasWithBothOptions">
            Quick Instructions
          </Button>
        </div>
      </div>
    );
  }
}
