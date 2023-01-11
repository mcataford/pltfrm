use clap::Parser;
use serde::Deserialize;

use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;
use std::path::Path;
use std::process::Command;

const DEFAULT_CONFIG_PATH: &str = "~/.config/pltfrm/pltfrm.json";

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(long)]
    cwd: Option<String>,

    #[arg(short, long)]
    build: bool,
    action: String,
    targets: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct Configuration {
    projects: HashMap<String, String>,
}

fn expand_tilde(path: String) -> String {
    let home_dir = std::env::var("HOME").unwrap();

    return home_dir + path.strip_prefix("~").unwrap();
}

fn start_containers(projects: Vec<String>, configuration: Configuration, build: bool) {
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

        let _status = command.status();
        // FIXME: Handle error statuses.
        println!("{} started.", project);
    }
}

fn stop_containers(projects: Vec<String>, configuration: Configuration) {
    for project in projects.iter() {
        let project_path = configuration
            .projects
            .get(project)
            .expect("Unknown project");
        let _status = Command::new("docker-compose")
            .current_dir(project_path)
            .arg("down")
            .status();
        // FIXME: Handle error statuses.
        println!("{} stopped.", project);
    }
}

fn main() {
    let cli = Args::parse();

    let config_path_raw = cli
        .cwd
        .unwrap_or(expand_tilde(DEFAULT_CONFIG_PATH.to_string()));

    let config_path = Path::new(&config_path_raw);

    if !config_path.exists() {
        panic!("No config");
    }

    let config_file = File::open(config_path).expect("Failed to open configuration file");
    let config_buf = BufReader::new(config_file);

    let config: Configuration =
        serde_json::from_reader(config_buf).expect("Failed to parse configuration. Expected json.");

    match cli.action.as_str() {
        "start" => start_containers(cli.targets, config, cli.build),
        "stop" => stop_containers(cli.targets, config),
        _ => panic!("Unknown command"),
    }
}
