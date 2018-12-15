import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Plan extends React.Component
{
  state = {
      plan_list: [],
      plan: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { plan_list: [], plan: null } );
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
          data.config_values = Object.keys( data.config_values ).map( ( key ) => ( [ key, data.config_values[ key ] ] ) );
          this.setState( { plan: data } );
        } );
    }
    else
    {
      props.listGet()
        .then( ( result ) =>
        {
          var plan_list = [];
          for ( var name in result.data )
          {
            var plan = result.data[ name ];
            name = CInP.extractIds( name )[0];
            plan_list.push( { name: name,
                              description: plan.description,
                              created: plan.created,
                              updated: plan.updated,
                            } );
          }

          this.setState( { plan_list: plan_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var plan = this.state.plan;
      return (
        <div>
          <h3>Plan Detail</h3>
          { plan !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ plan.name }</td></tr>
                  <tr><th>Description</th><td>{ plan.description }</td></tr>
                  <tr><th>Enabled</th><td>{ plan.enable }</td></tr>
                  <tr><th>Hostname Pattern</th><td>{ plan.hostname_pattern }</td></tr>
                  <tr><th>Config Values</th><td><table><thead/><tbody>{ plan.config_values.map( ( value ) => ( <tr key={ value[0] }><th>{ value[0] }</th><td>{ value[1] }</td></tr> ) ) }</tbody></table></td></tr>
                  <tr><th>Script</th><td><pre>{ plan.script }</pre></td></tr>
                  <tr><th>Complex List</th><td>{ plan.complex_list }</td></tr>
                  <tr><th>BluePrint List</th><td>{ plan.blueprint_list }</td></tr>
                  <tr><th>TimeSeries List</th><td>{ plan.timeseries_list }</td></tr>
                  <tr><th>Static Values</th><td>{ plan.static_values }</td></tr>
                  <tr><th>Slots Per Complex</th><td>{ plan.slots_per_complex }</td></tr>
                  <tr><th>Change Cooldown</th><td>{ plan.change_cooldown }</td></tr>
                  <tr><th>Max Inflight</th><td>{ plan.max_inflight }</td></tr>
                  <tr><th>Last Change</th><td>{ plan.last_change }</td></tr>
                  <tr><th>Nonce Counter</th><td>{ plan.nonce_counter }</td></tr>
                  <tr><th>Can Move</th><td>{ plan.can_move }</td></tr>
                  <tr><th>Can Destroy</th><td>{ plan.can_destroy }</td></tr>
                  <tr><th>Can Build</th><td>{ plan.can_build }</td></tr>
                  <tr><th>Created</th><td>{ plan.created }</td></tr>
                  <tr><th>Updated</th><td>{ plan.updated }</td></tr>
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
          <TableCell>Name</TableCell>
          <TableCell>Description</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.plan_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/plan/' + item.name }>{ item.name }</Link></TableCell>
            <TableCell>{ item.description }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Plan;
