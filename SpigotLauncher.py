# Python
import os, sys, subprocess

# Third Party
import toml, requests

program_version = 1.0
config_file_name = "SpigotLauncher.toml"


def halt_program(optional_message):
    if optional_message != "":
        print(optional_message)

    print("\nProgram will now halt.")
    sys.exit()


def write_config(toml_object):
    with open(config_file_name, "w") as config_file:
        toml.dump(toml_object, config_file)


def load_config(): 
    return toml.load(config_file_name)


def generate_config():
    config_template = {
        "general": {
            "debug": False,
            "pause_on_jar_closure": False,
            "java_path": "default",
            "java_initial_allocation_xms": 256,
            "java_max_allocation_xmx": 1536,
            "jar_preffix": "spigot",
            "use_last_jar_found": True
        },

        "paper_auto_upgrade": {
            "enabled": True,
            "desired_version": "1.18.2",
            "file_name": "paper-latest",
            "current_version": 0
        }
    }

    write_config(config_template)
    

if __name__ == "__main__":
    print(f"Japa's Spigot Launcher v{program_version}\n")

    if not os.path.exists("SpigotLauncher.toml"):
        print("No config file found! Generating one... ", end="")
        generate_config()
        print("Ok!\n")

    print("Loading Config File... ", end="")

    config = load_config()

    print("Ok!\n")

    debug = config["general"]["debug"]
    jar_file = ""
    
    # If Paper is Enabled, check for a new version (and updates if necessary), then use the Paper Spigot JAR
    if config["paper_auto_upgrade"]["enabled"]:
        print("Paper Auto Update is Enabled! Checking for new version... ", end="")

        current_version = config["paper_auto_upgrade"]["current_version"]
        desired_version = config["paper_auto_upgrade"]["desired_version"]

        desired_version_file_name = config["paper_auto_upgrade"]["file_name"] + ".jar"
        desired_version_url = f"https://papermc.io/api/v2/projects/paper/versions/{desired_version}"

        fetched_versions = requests.get(desired_version_url).json()["builds"]
        latest_version = fetched_versions[len(fetched_versions) - 1]

        jar_file = desired_version_file_name

        if current_version < latest_version:
            print("New Version found!")
            print(f"Downloading Version {latest_version}... ", end="")

            fetched_version_file = requests.get(f"{desired_version_url}/builds/{latest_version}/downloads/paper-{desired_version}-{latest_version}.jar")
            
            with open(desired_version_file_name, "wb") as file:
                file.write(fetched_version_file.content)

                config["paper_auto_upgrade"]["current_version"] = latest_version
                write_config(config)

                print("Ok!")

        else:
            print("No new version found.")

    # Else searches for a JAR file with the Preffix on the config
    else:
        current_directory = os.getcwd()
        current_directory_files = os.listdir(current_directory)
        jar_preffix = config["general"]["jar_preffix"]
        jar_array = []

        use_last_jar_found = config["general"]["use_last_jar_found"]

        # Iterates through every JAR on the current directory, if "use_last_jar_found" is false use the first JAR found
        for file_name in current_directory_files:
            if jar_preffix in file_name:
                if use_last_jar_found:
                    jar_array.append(file_name)

                else:
                    # Sets the JAR file and stops the unecessary looping
                    jar_file = file_name
                    break

        # If the loop was not stopped beforehand because of "use_last_jar_found", tries to use the last JAR
        if use_last_jar_found:
            if len(jar_array) == 0:
                halt_program(f"""ERROR: NO JAR FOUND WITH "{jar_preffix}" AS THE PREFFIX!""")

            else:
                jar_file = jar_array[len(jar_array) - 1]

    # Default is java, changes if the java_path is not "default"
    java_executable = "java"
    
    if config["general"]["java_path"] != "default":
        java_executable = config["general"]["java_path"] + "javaw.exe"

    java_initial_allocation_xms = config["general"]["java_initial_allocation_xms"]
    java_max_allocation_xmx = config["general"]["java_max_allocation_xmx"]

    if debug:
        print(f"Selected JAR: {jar_file}")
        print(f"Initial Allocation: {java_initial_allocation_xms}")
        print(f"Max Allocation: {java_max_allocation_xmx}")

    print("\nStarting Minecraft server...\n")

    subprocess.Popen(f"{java_executable} -jar {jar_file} -Xms {java_initial_allocation_xms} -Xmx {java_max_allocation_xmx}").wait()

    if config["general"]["pause_on_jar_closure"]:
        print("\nPress any Key to close the program.")
        input()