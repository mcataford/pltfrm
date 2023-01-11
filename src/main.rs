use clap::Parser;
use owo_colors::OwoColorize;
use serde::Deserialize;

use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;
use std::io::{self, Write};
use std::path::Path;
use std::process::Command;

const DEFAULT_CONFIG_PATH: &str = "~/.config/pltfrm/pltfrm.json";

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Defines the path to the pltftm configuration file.
    #[arg(long)]
    config_path: Option<String>,

    /// If truthy, containers will be rebuilt before being started.
    #[arg(short, long)]
    build: bool,

    /// If truthy, all containers defined in the config are processed, targets are ignored.
    #[arg(short, long)]
    all: bool,

    /// If truthy, subcommand output is printed out after execution. Note that failure
    /// is always noisy.
    #[arg(short, long)]
    verbose: bool,

    /// Action to take.
    action: String,

    /// Collection of projects to apply the action on.
    targets: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct Configuration {
    projects: HashMap<String, String>,
}

/// Expands the ~ marker in paths to `$HOME`.
///
/// This effectively converts fancier paths into absolute ones.
fn expand_tilde(path: String) -> String {
    let home_dir = std::env::var("HOME").unwrap();

    return home_dir + path.strip_prefix("~").unwrap();
}

/// Starts the specified projects sequentially, in the order they are provided.
///
/// If the `build` flag is truthy, the containers are rebuilt before being started.
/// If the `verbose` flag is truthy, success output is always emitted to stdout.
fn start_containers(
    projects: Vec<String>,
    configuration: Configuration,
    build: bool,
    verbose: bool,
) {
    for project in projects.iter() {
        let project_path = configuration
            .projects
            .get(project)
            .expect("Unknown project");
        let mut command = Command::new("docker-compose");
        command.current_dir(project_path).arg("up").arg("-d");

        if build {
            command.arg("--build");
        }

        let output = command.output().expect("Failed to execute");

        if verbose {
            io::stdout().write_all(&output.stdout).unwrap();
            io::stderr().write_all(&output.stderr).unwrap();
        } else if !output.status.success() {
            io::stderr().write_all(&output.stderr).unwrap();
        }

        match output.status.success() {
            true => println!("{}", format!("{} started.", project).green()),
            false => println!("{}", format!("{} failed to start.", project).red()),
        }
    }
}

/// Stops the specified projects sequentially, in the order they are provided.
///
/// If the `verbose` flag is truthy, success output is always emitted to stdout.
fn stop_containers(projects: Vec<String>, configuration: Configuration, verbose: bool) {
    for project in projects.iter() {
        let project_path = configuration
            .projects
            .get(project)
            .expect("Unknown project");
        let mut command = Command::new("docker-compose");
        command.current_dir(project_path).arg("down");

        let output = command.output().expect("Failed to execute");

        if verbose {
            io::stdout().write_all(&output.stdout).unwrap();
            io::stderr().write_all(&output.stderr).unwrap();
        } else if !output.status.success() {
            io::stderr().write_all(&output.stderr).unwrap();
        }

        match output.status.success() {
            true => println!("{}", format!("{} stopped.", project).green()),
            false => println!("{}", format!("{} failed to stop.", project).red()),
        }
    }
}

/// Gets the configuration from the specific path if it exists.
///
/// If no path is provided, the default path (`DEFAULT_CONFIG_PATH`) is used instead.
/// Note that a configuration must exist for pltfrm to run.
fn get_configuration(path: Option<String>) -> Configuration {
    let config_path_raw = path.unwrap_or(expand_tilde(DEFAULT_CONFIG_PATH.to_string()));

    let config_path = Path::new(&config_path_raw);

    if !config_path.exists() {
        panic!("No config");
    }

    let config_file = File::open(config_path).expect("Failed to open configuration file");
    let config_buf = BufReader::new(config_file);

    return serde_json::from_reader(config_buf)
        .expect("Failed to parse configuration. Expected json.");
}

fn main() {
    let cli = Args::parse();

    let config: Configuration = get_configuration(cli.config_path);

    let target_projects = match cli.all {
        true => config
            .projects
            .keys()
            .map(|project| project.to_string())
            .collect(),
        false => cli.targets,
    };

    match cli.action.as_str() {
        "start" => start_containers(target_projects, config, cli.build, cli.verbose),
        "stop" => stop_containers(target_projects, config, cli.verbose),
        _ => panic!("Unknown command"),
    }
}
