import React, { Component } from 'react';
import './Error.css';
import dimeGray from './dimeGray.png';
import { motion } from "framer-motion";
import { Container, LinearProgress, Stack } from '@mui/material';
import { Link } from 'react-router-dom';

export default class Error extends Component {
  componentDidMount() {
    this.props.setActiveLink("error");
  }

  render() {
    return (
      <div
        className="app-error-page">
        <header className="app-error-page-header">
          <div>
            <Stack sx={{ width: '100%', color: 'grey.500' }} spacing={2}>
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.6, ease: 'backInOut' }}
              >
                <img src={dimeGray} className="app-error-page-logo" alt="logo" />
              </motion.div>
              {this.props.status ?
                <Container>
                  <LinearProgress color="inherit" className='mx-4' sx={{ borderRadius: 2 }} />
                </Container>
                :
                <>
                  <motion.h6
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}>
                    {`Page Not found. Go Back to the `}
                    <Link
                      to="/"
                      className={'material-red-f'}
                      style={{ textDecoration: "none" }}
                      role={'button'}
                    >
                      Dashboard
                    </Link>
                  </motion.h6>
                </>
              }
            </Stack>
          </div>
        </header>
      </div>
    );
  }
}
