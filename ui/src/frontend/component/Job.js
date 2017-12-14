import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Job extends React.Component
{
  state = {
      job_list: [],
      job: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { job_list: [], job: null } );
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
          data.action = CInP.extractIds( data.action )[0]; 
          this.setState( { job: data } );
        } );
    }
    else
    {
      props.listGet()
        .then( ( result ) =>
        {
          var job_list = [];
          for ( var id in result.data )
          {
            var job = result.data[ id ];
            id = CInP.extractIds( id )[0];
            job_list.push( { id: id,
                                action: job.action,
                                task: job.task,
                                state: job.state,
                                created: job.created,
                                updated: job.updated,
                              } );
          }

          this.setState( { job_list: job_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var job = this.state.job;
      return (
        <div>
          <h3>Job Detail</h3>
          { job !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Action</th><td><Link to={ '/action/' + job.action }>{ job.action }</Link></td></tr>
                  <tr><th>Target</th><td>{ job.target }</td></tr>
                  <tr><th>Task</th><td>{ job.task }</td></tr>
                  <tr><th>State</th><td>{ job.state }</td></tr>
                  <tr><th>Created</th><td>{ job.created }</td></tr>
                  <tr><th>Updated</th><td>{ job.updated }</td></tr>
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
          <TableCell>Action</TableCell>
          <TableCell>Task</TableCell>
          <TableCell>State</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.job_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/job/' + item.id }>{ item.id }</Link></TableCell>
            <TableCell>{ item.action }</TableCell>
            <TableCell>{ item.task }</TableCell>
            <TableCell>{ item.state }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Job;
