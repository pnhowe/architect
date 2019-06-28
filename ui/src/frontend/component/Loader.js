import React from 'react';
import CInP from './cinp';
import { Button, List, ListItem, ListDivider } from 'react-toolbox';


class Loader extends React.Component
{
  state = {
      current_hash: '',
      last_update: '',
      upstream_hash: '',
      last_check: ''
  };

  loaderCheck = () =>
  {
    this.props.loaderCheck()
    .then( ( results ) =>
    {
      this.update( this.props );
    },
    ( error ) => alert( 'Error Checking Project: "' + error.reason + '": "' + error.detail + '"' ) );
  };

  loaderUpdate = () =>
  {
    this.props.loaderUpdate()
    .then( ( result ) =>
    {
      this.update( this.props );
    },
    ( error ) => alert( 'Error Updating Project: "' + error.reason + '": "' + error.detail + '"' ) );
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { current_hash: '', last_update: '', upstream_hash: '', last_check: '' } );
    this.update( newProps );
  }

  update( props )
  {
    props.getLoader()
      .then( ( result ) =>
      {
        this.setState( { current_hash: result.data.current_hash, last_update: result.data.last_update, upstream_hash: result.data.upstream_hash, last_check: result.data.last_check } );
      } );
  }

  render()
  {
    return (
      <List>
        <ListItem><Button onClick={ this.loaderCheck }>Check</Button></ListItem>
        <ListItem><Button onClick={ this.loaderUpdate }>Update</Button></ListItem>
        <ListDivider />
        <ListItem><div><strong>Current Hash:</strong> { this.state.current_hash }</div></ListItem>
        <ListItem><div><strong>Last Update:</strong> { this.state.last_update }</div></ListItem>
        <ListItem><div><strong>Upstream Hash:</strong> { this.state.upstream_hash }</div></ListItem>
        <ListItem><div><strong>Last Check:</strong> { this.state.last_check }</div></ListItem>
      </List>
    );

  }
};

export default Loader;
