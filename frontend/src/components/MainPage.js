import React from 'react';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import GameChoose from './GameChoose';
import Box from '@mui/system/Box';
import { connect } from 'react-redux';
import Comparator from './Comparator';
import Instructor from './Instructor';

class MainPage extends React.Component{
  renderComparator = () => {
    //  ---filipchuk.al 24.11.2025---
    //  Упрощено условие: вместо сравнения с null проверяется значения на пустоту через отрицание (!)
    // if (this.props['left_team'] === null || this.props['team_id'] === null) {
    if (!this.props.left_team || !this.props.right_team) {
    //  -----------------------------
      return <Instructor/>
    }
    return (
      <Box>
        <Comparator/>
      </Box>
    ) 
  }

  render = () => {
    return (
      <Stack direction="row" justifyContent='space-evenly'>
          <Box style={{height: '100vh', overflow: 'auto', width: '32%'}}>
              <GameChoose/>
          </Box>
          <Paper evaluation={1} style={{height: '100vh', overflow: 'auto', width: '64%'}}>
              {this.renderComparator()}
          </Paper>
      </Stack>
    )
  }
}

export default connect(
  store => ({
      left_team : store.left_team,
      right_team : store.right_team,
  })
)(MainPage);