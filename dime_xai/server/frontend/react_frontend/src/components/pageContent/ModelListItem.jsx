import React, { Component } from 'react';
import DeleteModal from '../modal/DeleteModal';
import ViewInArIcon from '@mui/icons-material/ViewInAr';
import {
  Box,
  Button,
  Chip,
  Divider,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stack,
} from '@mui/material';
import { Cancel } from '@mui/icons-material';

export default class ModelListItem extends Component {
  render() {
    return (
      <Box
        key={this.props.modelName}>
        <ListItem
          className="w-100 app-model-list-item"
        >
          <ListItemIcon>
            <ViewInArIcon />
          </ListItemIcon>
          <ListItemText
            id="switch-list-label-wifi"
            primary={this.props.modelName}
            secondary={this.props.modelSize} />
          {this.props.compatibilityChip &&
            <Chip
              label="DIME Compatible"
              color="success"
              className="material-green" />
          }
          <Stack direction="row" spacing={1} className={"float-end"}>
            <Button
              variant='outlined'
              className="float-end app-button app-button-red model-list-button"
              sx={{ border: "none", '&:hover': { border: "none" } }}
              startIcon={<Cancel />}
              data-bs-toggle="modal"
              data-bs-target={`#${this.props.modelId}`}>
              Delete
            </Button>
          </Stack>
        </ListItem>
        <Divider component="li" variant='fullWidth' />
        <DeleteModal
          id={`${this.props.modelId}`}
          title={`Delete Model`}
          body={`Do you want to permenently delete the Model ${this.props.modelName}?`}
          item={`${this.props.modelName}`}
          deleteHandler={this.props.handleDelete}
          buttonPrimary={{
            button: true,
            buttonClass: 'app-button-red model-delete-modal-button model-delete-modal-button-primary',
            buttonType: 'error',
            buttonVarient: 'contained',
            buttonText: 'Confirm',
          }}
          buttonSecondary={{
            button: true,
            buttonClass: 'app-button-steel model-delete-modal-button model-delete-modal-button-secondary',
            buttonType: 'secondary',
            buttonVarient: 'contained',
            buttonText: 'Deny',
          }} />
      </Box>
    );
  }
}
