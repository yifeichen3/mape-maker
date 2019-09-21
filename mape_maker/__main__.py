import os
import sys
import click
#import MapeMaker as MapeMaker
from mape_maker import MapeMaker 
from datetime import datetime as dt


def click_callback(f):
    return lambda _, __, x: f(x)


def check_date(s):
    try:
        return dt.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise Exception(msg)
    except TypeError:
        print("")
        return None


@click.command()
@click.argument('input_file')
@click.option('--target_mape', "-t",  default=None, type=float, help='mape you want in return otherwise will take the mape of the dataset')
@click.option('--simulated_timeseries','-st', default="forecasts", help="feature you want to simulate 'actuals' or 'forecasts'")
@click.option('--base_process', '-bp', default="ARMA", help="method used to this end 'iid' or 'ARMA")
@click.option('--a', '-a', default=4, type=float, help="percent of data on the left or on the right for the estimation")
@click.option('--output_dir', "-o", default=None, help="path to a directory to save the simulations")
@click.option('--number_simulations', '-n', default=1, help="number of simulations")
@click.option('--input_start_dt', '-is', default=None, callback=click_callback(check_date), help="start_date for the computation of the distributions, format='Y-m-d %H:%M:%S' ")
@click.option('--input_end_dt', '-ie', default=None, callback=click_callback(check_date), help="end_date for the computation of the distributions, format='Y-m-d %H:%M:%S'")
@click.option('--simulation_start_dt', '-sd', default=None, callback=click_callback(check_date), help="start_date for the simulation, format='Y-m-d %H:%M:%S' ")
@click.option('--simulation_end_dt', '-ed', default=None, callback=click_callback(check_date), help="end_date for the simulation, format='Y-m-d %H:%M:%S'")
@click.option('--title', '-ti', default=None, help="title for the plot")
@click.option('--seed', '-s', default=None, help="random seed")
@click.option('--load_pickle', '-lp', default=False, type=bool, help="Load the pickle file instead of estimating")
@click.option('--curvature', '-c', default=False, help="curvature")
@click.option('--time_limit', '-tl', default=3600, help="time limit of the computation of curvature")
@click.option('--curvature_target', '-ct', default=None, type=float, help="the target of the second difference")
@click.option('--mip_gap', '-m', default=0.3, type=float, help="the curvature mip gap")
@click.option('--solver', '-so', default="gurobi", help="curvature solver")
###@click.option('--full_dataset', '-fd', default=False, type=bool, help="simulation over all the dataset")
@click.option('--latex_output', '-lo', default=False, type=bool, help="write results in latex file")
@click.option('--show', '-sh', default=True, type=bool, help="plot simulations")
def main(input_file, target_mape, simulated_timeseries, base_process, a, output_dir, number_simulations, input_start_dt,
         input_end_dt, simulation_start_dt, simulation_end_dt, title, seed, load_pickle, curvature, time_limit, curvature_target,
         mip_gap, solver, latex_output, show):
    return main_func(input_file, target_mape, simulated_timeseries, base_process, a, output_dir, number_simulations,
                     input_start_dt, input_end_dt, simulation_start_dt, simulation_end_dt, title, seed, load_pickle,
                     curvature, time_limit, curvature_target, mip_gap, solver, latex_output, show)

def input_check(input_start_dt, input_end_dt, simulation_start_dt, simulation_end_dt, output_dir):
    """ Check some of the user inputs.
        TBD: get better date handling; delete this comment after Dec 2019
    """
    if (input_start_dt is None and input_end_dt is not None) \
       or (input_start_dt is not None and input_end_dt is None):
        raise RuntimeError\
            ("You must give both or neither of the input dates")
    if (simulation_start_dt is None and simulation_end_dt is not None) \
       or (simulation_start_dt is not None and simulation_end_dt is None):
        raise RuntimeError\
            ("You must give both or neither of the simulation dates")
    if simulation_start_dt is not None\
       and input_start_dt is not None\
       and simulation_start_dt < input_start_dt:
        raise RuntimeError ("Simulation must start after input start")
    if output_dir is not None and os.path.exists(output_dir):
        raise RuntimeError ("Output directory={} already exists".format(output_dir))

def main_func(input_file, target_mape, simulated_timeseries, base_process, a, output_dir, number_simulations, input_start_dt,
              input_end_dt, simulation_start_dt, simulation_end_dt, title, seed, load_pickle, curvature, time_limit, curvature_target,
         mip, solver, latex_output, show):

    input_check(input_start_dt, input_end_dt, simulation_start_dt, simulation_end_dt, output_dir)
    if simulation_start_dt is None and input_start_dt is not None:
        simulation_start_dt = input_start_dt
    if simulation_end_dt is None and input_end_dt is not None:
        simulation_end_dt = input_end_dt
    full_dataset = simulation_start_dt is None and simulation_end_dt is None
        
    mare_embedder = MapeMaker.MapeMaker(path=input_file,
                                        ending_feature=simulated_timeseries,
                                        load_pickle=load_pickle,
                                        seed=seed,
                                        input_start_dt=input_start_dt,
                                        input_end_dt=input_end_dt)
    if curvature:
        pyomo_parameters = {
                "MIP": mip,
                "time_limit": time_limit,
                "curvature_target": curvature_target,
                "solver": solver,
            }
    else:
        pyomo_parameters = None

    if target_mape is not None:
        target_mape = target_mape/100

    list_of_date_ranges = [[simulation_start_dt, simulation_end_dt]]
    scores = mare_embedder.simulate(target_mare=target_mape, base_process=base_process, n=number_simulations,
                                    full_dataset=full_dataset, output_dir=output_dir,
                                    list_of_date_ranges=list_of_date_ranges, curvature_parameters=pyomo_parameters,
                                    latex=latex_output)

    t = mare_embedder.r_tilde
    text = "Dataset used : {}\n" \
           "Computed Mape from the dataset {}%\n" \
           "Mape fit from the dataset {}%\n" \
           "Target Mape : {}%\n" \
           "Simulated from {} to {}\n" \
           "With base process {}\n" \
           "Computed {} simulations from {} to {}".format(input_file,
                                                          round(100*mare_embedder.mare,2),
                                                          round(100*mare_embedder.r_m_hat,2), round(100*t,2),
                                                          mare_embedder.x, mare_embedder.y, base_process,
                                                          number_simulations, mare_embedder.start_date.strftime("%Y-%m-%d"),
                                                          mare_embedder.end_date.strftime("%Y-%m-%d"))

    print(text)

    mare_embedder.save_all_outputs(output_dir)
    if output_dir is not None:
        text = text + "\nOutput stored in directory {}".format(output_dir)

    if show:
        mare_embedder.plot_example(title=title)


if __name__ == "__main__":
    main()


