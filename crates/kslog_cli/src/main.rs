use std::{env, process::ExitCode};

fn main() -> ExitCode {
    match kslog_cli::run_cli(env::args().skip(1)) {
        Ok(output) => {
            println!("{output}");
            ExitCode::SUCCESS
        }
        Err(error) => {
            eprintln!("{error}");
            ExitCode::from(1)
        }
    }
}
