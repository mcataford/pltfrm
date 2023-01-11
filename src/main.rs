use clap::Parser;
use serde::Deserialize;

use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;
use std::path::Path;
use std::process::Command;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(long)]
    cwd: Option<String>,
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

fn start_containers(projects: Vec<String>, configuration: Configuration) {
    for project in projects.iter() {
        let project_path = configuration.projects.get(project).expect("wowow");
        let status = Command::new("docker-compose")
            .current_dir(project_path)
            .arg("up")
            .arg("-d")
            .status();
        println!("{} started.", project);
    }
}

fn stop_containers(projects: Vec<String>, configuration: Configuration) {
    for project in projects.iter() {
        let project_path = configuration.projects.get(project).expect("wowow");
        let status = Command::new("docker-compose")
            .current_dir(project_path)
            .arg("down")
            .status();
        println!("{} stopped.", project);
    }
}

fn main() {
    let cli = Args::parse();

    let config_path_raw = cli.cwd.unwrap_or(expand_tilde("~/.config/pltfrm/pltfrm.json".to_string()));

    let config_path = Path::new(&config_path_raw);
    
    if !config_path.exists() {
        panic!("No config");
    }

    let config_file = File::open(config_path).expect("w");
    let config_buf = BufReader::new(config_file);

    let config: Configuration = serde_json::from_reader(config_buf).expect("wo");

    if cli.action == "start" {
        start_containers(cli.targets, config);
    } else if cli.action == "stop" {
        stop_containers(cli.targets, config);
    }
}
