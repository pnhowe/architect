import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Instance extends React.Component
{
  state = {
      instance_list: [],
      instance: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { instance_list: [], instance: null } );
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
          data.plan = CInP.extractIds( data.plan )[0];
          this.setState( { instance: data } );
        } );
    }
    else
    {
      props.listGet()
        .then( ( result ) =>
        {
          var instance_list = [];
          for ( var id in result.data )
          {
            var instance = result.data[ id ];
            id = CInP.extractIds( id )[0];
            instance_list.push( { id: id,
                                plan: instance.plan,
                                hostname: instance.hostname,
                                state: instance.state,
                                created: instance.created,
                                updated: instance.updated,
                              } );
          }

          this.setState( { instance_list: instance_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var instance = this.state.instance;
      return (
        <div>
          <h3>Instance Detail</h3>
          { instance !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Hostname</th><td>{ instance.hostname }</td></tr>
                  <tr><th>Plan</th><td><Link to={ '/plan/' + instance.plan }>{ instance.plan }</Link></td></tr>
                  <tr><th>Nonce</th><td>{ instance.nonce }</td></tr>
                  <tr><th>Complex</th><td>{ instance.complex }</td></tr>
                  <tr><th>BluePrint</th><td>{ instance.blueprint }</td></tr>
                  <tr><th>Foundation Id</th><td>{ instance.foundation_id }</td></tr>
                  <tr><th>Structure Id</th><td>{ instance.structure_id }</td></tr>
                  <tr><th>Created</th><td>{ instance.created }</td></tr>
                  <tr><th>Updated</th><td>{ instance.updated }</td></tr>
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
          <TableCell>Plan</TableCell>
          <TableCell>Hostname</TableCell>
          <TableCell>State</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.instance_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/instance/' + item.id }>{ item.id }</Link></TableCell>
            <TableCell>{ item.plan }</TableCell>
            <TableCell>{ item.hostname }</TableCell>
            <TableCell>{ item.state }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Instance;
