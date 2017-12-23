import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Action extends React.Component
{
  state = {
      action_list: [],
      action: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { action_list: [], action: null } );
    this.update( newProps );
  }

  update( props )
  {
    if( props.id !== undefined )
    {
      props.detailGet( props.id )
       .then( ( result ) =>
        {
          var data = result.data;
          data.instance = CInP.extractIds( data.instance )[0]; 
          this.setState( { action: data } );
        } );
    }
    else
    {
      props.listGet()
        .then( ( result ) =>
        {
          var action_list = [];
          for ( var id in result.data )
          {
            var action = result.data[ id ];
            id = CInP.extractIds( id )[0];
            action_list.push( { id: id,
                                instance: action.instance,
                                action: action.action,
                                progress: action.progress,
                                created: action.created,
                                updated: action.updated,
                              } );
          }

          this.setState( { action_list: action_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var action = this.state.action;
      return (
        <div>
          <h3>Action Detail</h3>
          { action !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Instance</th><td><Link to={ '/instance/' + action.instance }>{ action.instance }</Link></td></tr>
                  <tr><th>Action</th><td>{ action.action }</td></tr>
                  <tr><th>State</th><td>{ action.state }</td></tr>
                  <tr><th>Progress</th><td>{ action.progress }</td></tr>
                  <tr><th>Created</th><td>{ action.created }</td></tr>
                  <tr><th>Updated</th><td>{ action.updated }</td></tr>
                </tbody>
              </table>
            </div>
          }
        </div>
      );
    }

    return (
      <Table selectable={ false } multiSelectable={ false }>
        <TableHead>
          <TableCell>Id</TableCell>
          <TableCell>Instance</TableCell>
          <TableCell>Action</TableCell>
          <TableCell>Progress</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.action_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/action/' + item.id }>{ item.id }</Link></TableCell>
            <TableCell>{ item.instance }</TableCell>
            <TableCell>{ item.action }</TableCell>
            <TableCell>{ item.progress }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Action;
