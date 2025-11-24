import React from 'react';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import { connect } from 'react-redux';

//  ---filipchuk.al 24.11.2025---
// Добавлена проверка формата logo: если путь уже абсолютный (http/https), используем его, иначе подставляем домен khl.ru
const renderLogoName = (team) => {
  // Если logo начинается с 'http' или '//', оставляем как есть
  let image = team['logo'].startsWith('http') || team['logo'].startsWith('//')
    ? team['logo'].replace(/^\/+/, 'https://')  // меняем // на https://
    : 'http://khl.ru/' + team['logo'];

  return (
    <Stack direction='column' style={{ width: '40%' }}>
      <Box
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
        justifyContent='center'
      >
        <img 
          src={image}
          style={{ width: '18vh', height: '18vh' }}
          alt={team['name']}
        />
      </Box>
      <Box style={{ display: 'flex', alignItems: 'center', fontSize: 18 }} justifyContent='center'>
        {team['team']}
      </Box>
      <Box style={{ display: 'flex', alignItems: 'center', fontSize: 12 }} justifyContent='center'>
        {team['city']}
      </Box>
    </Stack>
  )
}
//  -----------------------------

class TeamsPreview extends React.Component {
  getColor = (stats_0, stats_1) => {
    let v1 = parseFloat(stats_0['value']);
    let v2 = parseFloat(stats_1['value']);
    let better = stats_0['better'];
    if ((v1 < v2 && better === 'less') || (v1 > v2 && better === 'more')) {
      return '#B5B8B1'
    }
    return '#FFFFFF';
  }

  render = () => {
    console.log('http://khl.ru/' + this.props.left_team['logo']);

    return (
      <Stack direction="row" 
        justifyContent="space-evenly" 
        sx={{ m: 0 }}
        spacing={0.5}
        style={{
          width: "100%"
        }}
      >
        {renderLogoName(this.props.left_team)}
        <Box
          style={{
            width: '20%',
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
          }}
          justifyContent='center'
        >
          VS
        </Box>
       {renderLogoName(this.props.right_team)}
      </Stack>
    )
  }
}


export default connect(
  store => ({
      left_team : store.left_team,
      right_team : store.right_team,
  })
)(TeamsPreview);


