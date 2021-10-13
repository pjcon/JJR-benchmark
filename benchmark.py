#!/bin/env python

"""



"""

import os
import shutil
import time
import datetime
import logging
import pathlib
import subprocess

import numpy as np

config = {
        'experiment_dir': './tests',
        'log_file': './tests/log',
        'results_file': './results.csv',
        'n_records_start': 100,
        'n_records_stop': 1000,
        'n_steps': 10,
        'n_repeat': 1,
        'schedule': 'linear', # linear/exponential/power10
        'results_key': [ 'procedure_time',
                         'num_records_generated', 
                         'num_job_pre', 'num_job_post',
                         'num_blahd_pre', 'num_blahd_post',
                         'num_event_pre', 'num_event_post',
                         ],
        'delete_old_records':True 
}

def get_datetime():
    return datetime.datetime.now()

def mkschedule(start, stop, n, r, method='exponential'):
    rng = stop - start

    if method == 'exponential':
        return np.array([start+np.power(rng, i/(n-1))-1 for i in np.arange(n)], dtype=int).repeat(r)
    elif method == 'linear':
        return np.array([start+rng*(i)/(n-1) for i in np.arange(n)], dtype=int).repeat(r)
    elif method == 'power10':
        return np.array([start+np.power(rng, i/(n-1))-1 for i in np.arange(n)], dtype=int).repeat(r)

def write_results(session, results_file, results):
    logging.info(f'Date: {get_datetime()}')
    logging.info(f'Writing results to: {results_file}')
    with open(results_file, 'a') as res:
        res.write(f'Session: {session}\n')

        res.write(','.join(config['results_key']) + '\n')
        for r in results:
            res.write(','.join([str(k) for k in r]) + '\n')

def generate_records(n, dir):
    from bin.gen_records import JoinJobRecordsGenerator
    jjrg = JoinJobRecordsGenerator(n, 1, dir)
    jjrg.write_messages('csv')

def copy_records_old(src):
    dest = '/var/lib/mysql/clientdb'

    for parent, dirs, files in os.walk(src, topdown=False):

        if not files:
            continue

        ffrom = os.path.join(parent, files[0])
        filename = os.path.basename(parent).split('-')[0] + '.csv'

        fto = os.path.join(dest, filename)

        logging.debug(f'Copy {ffrom} -> {fto}')

        shutil.copy(ffrom, fto)

def copy_records(src):
    subprocess.call(['bin/call_transfer.sh', str(src), '/var/lib/mysql/clientdb'])

def delete_all_records():
    subprocess.call(['bin/call_delete_data.sh', 'all'])

def delete_new_records():
    subprocess.call(['bin/call_delete_data.sh', 'new'])

def load_records():
    subprocess.call(['bin/call_load_data.sh'])

def call_procedure(n=''):
    subprocess.call(['bin/call_procedure.sh', str(n)])

def count_records():
    return [int(i) for i in subprocess.check_output(['./bin/call_count_records.sh']).decode().split('\n') if i.isnumeric()]

#def write_results(**kwargs): # kwargs should match results key
    #pass


def run(n, dir='./'):

    logging.debug('Generating records.')
    generate_records(n, dir)

    logging.debug('Transferring records.')
    copy_records(dir)

    if config['delete_old_records']:
        logging.debug(f'Deleting all records.')
        delete_all_records()

    logging.debug('Loading records.')
    load_records()

    logging.debug(f'Counting records...')
    num_job_pre, num_blahd_pre, num_event_pre = count_records()

    logging.debug(f'Running procedure...')

    run_start = time.time()
    call_procedure()
    run_time = time.time() - run_start
    
    logging.debug(f'Counting records...')
    num_job_post, num_blahd_post, num_event_post = count_records()

    num_job_post = count_records()

    #write_results(num_records_generated=n, num_jobrecords_processed)

    with open(dir/'result', 'w') as f:
        f.write(f'procedure_time: {run_time}\n')
        f.write(f'num_records_generated: {n}\n')
        f.write(f'num_blahd_pre: {num_rec_pre}\n')
        f.write(f'num_blahd_post: {num_rec_post}\n')
        f.write(f'num_event_pre: {num_event_pre}\n')
        f.write(f'num_event_post: {num_event_post}\n')
        f.write(f'num_job_pre: {num_job_pre}\n')
        f.write(f'num_job_post: {num_job_post}\n')


    logging.info(f'time {run_time}, processed: {num_jobrecords}')
    return num_jobrecords, run_time


def experiment():

    print(count_records())
    return

    results = []
    for i, n in enumerate(schedule):
        logging.info(f'Run: {i}')

        run_dir = session_dir / f'run.{i}'
        run_dir.mkdir(exist_ok=False)

        k, t = run(n, dir=run_dir)

        results.append((n, k, t))

    return results


exp_dir = pathlib.Path(config['experiment_dir'])
session_dir = exp_dir / f'session.{len(os.listdir(exp_dir))}.{int(get_datetime().timestamp())}'

exp_dir.mkdir(exist_ok=True)
session_dir.mkdir(exist_ok=True)

logging.basicConfig(filename=config['log_file'], 
                    filemode='a',
                    encoding='utf-8',
                    level=logging.DEBUG)
                    #format="%(asctime)s:%(levelname)s:%(module)s:%(messages)s")


if __name__ == '__main__':
    results = experiment()
    exit(0)

    start_time = get_datetime()
    logging.info(f'Session: {start_time}')
    logging.info(f'Config: {config}')

    schedule = mkschedule(config['n_records_start'],
                          config['n_records_stop'], 
                          config['n_steps'], config['n_repeat'], 
                          method=config['schedule'])

    logging.info(f'Schedule: {list(schedule)}')

    results = experiment()


    finish_time = get_datetime()
    session_time = finish_time.timestamp() - start_time.timestamp()
    logging.info(f'Session time: {session_time}')

    logging.info(f'Writing file.')

    results_file = session_dir / config['results_file']
    write_results(session_dir, results_file, results)
    shutil.copy(results_file, config['results_file'])

    logging.info(f'Finished: {finish_time}')
