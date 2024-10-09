import os
import json
import argparse
import subprocess
from zipfile import ZipFile


os_name = 'linux'
user_home_dir = os.path.expanduser('~')
launcher_name = 'MCLauncher'
game_dir = f'{user_home_dir}/.{launcher_name}'


def get_versions():
    return requests.get(version_manifest_url).json()['versions']


def extract_game_natives(version):
    version_json = f'{game_dir}/versions/{version}/{version}.json'
    with open(version_json) as file:
        data = json.loads(file.read())
        libraries = data['libraries']
        native_name = f'natives-{os_name}'
        natives_dir = f'{game_dir}/bin/natives/{version}'

        for library in libraries:
            download_obj = library['downloads']

            if 'classifiers' in download_obj:
                classifiers = download_obj['classifiers']
                
                if native_name in classifiers:
                    native = classifiers[native_name]
                    native_path = native['path']
                    lib_relative_path = f'{game_dir}/libraries/{native_path}'

                    # Create natives dir
                    if not os.path.exists(natives_dir):
                        os.makedirs(natives_dir)

                    # Extract natives
                    if os.path.exists(lib_relative_path):
                        native_archive = ZipFile(lib_relative_path, 'r')
                        [native_archive.extract(file, natives_dir) for file in native_archive.namelist() if file.endswith('.so')]
                        print(f'extracted {lib_relative_path} to {natives_dir}')
                    

def get_client_jar_path(version):
    return os.path.abspath(f'{game_dir}/versions/{version}/{version}.jar')


def get_game_libraries(version):
    libs = ''
    version_json = f'{game_dir}/versions/{version}/{version}.json'
    native_name = f'natives-{os_name}'

    with open(version_json) as file:
        data = json.loads(file.read())
        libraries = data['libraries']

        for library in libraries:
            download_obj = library['downloads']

            if 'artifact' in download_obj:
                lib_path = download_obj['artifact']['url'].replace("https://libraries.minecraft.net/", "")

            if 'classifiers' in download_obj:
                classifiers = download_obj['classifiers']
                if native_name in classifiers:
                    native = classifiers[native_name]
                    lib_path = native['url'].replace("https://libraries.minecraft.net/", "")
                
            lib_full_path = f'{game_dir}/libraries/{lib_path}'
            lib_abs_path = os.path.abspath(lib_full_path)
            
            index = libs.find(lib_abs_path)
            if index == -1:
                libs += lib_abs_path + ':'
            
    return libs


def get_client_main_class(version):
    version_json = f'{game_dir}/versions/{version}/{version}.json'
    with open(version_json) as file:
        data = json.loads(file.read())
        return data['mainClass']


def get_client_asset_index(version):
    version_json = f'{game_dir}/versions/{version}/{version}.json'
    with open(version_json) as file:
        data = json.loads(file.read())
        return data['assets']


def start_custom_version(version_name, game_version, username):
    print(f'starting Minecraft {version_name}\n')

    java_path = 'java'
    java_library_path = os.path.abspath(f'{game_dir}/bin/natives/{game_version}')
    
    client_jar_path = get_client_jar_path(version_name)
    client_libraries = f'{get_game_libraries(version_name)}{client_jar_path}'
    client_main_class = get_client_main_class(version_name)
    
    assets_dir = f'{game_dir}/assets'
    asset_index = get_client_asset_index(version_name)

    java_command = [
        java_path,
        f'-Djava.library.path={java_library_path}',
        f'-Dminecraft.client.jar={client_jar_path}',
        '-cp',
        client_libraries,
        '-Xmx2G',
        '-XX:+UnlockExperimentalVMOptions',
        '-XX:+UseG1GC',
        '-XX:G1NewSizePercent=20',
        '-XX:G1ReservePercent=20',
        '-XX:MaxGCPauseMillis=50',
        '-XX:G1HeapRegionSize=32M',
        client_main_class,
        '--username',
        username,
        '--version',
        version,
        '--gameDir',
        game_dir,
        '--assetsDir',
        assets_dir,
        '--assetIndex',
        asset_index,
        '--uuid',
        uuid,
        '--accessToken',
        token,
        '--userType',
        'legacy',
        '--userProperties',
        '{}'
    ]
    # print(' '.join(java_command))
    subprocess.run(java_command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python Minecraft Launcher')

    parser.add_argument('--version', type=str, required=True)
    parser.add_argument('--username', type=str, required=True)
    parser.add_argument('--uuid', type=str, default='0')
    parser.add_argument('--userType', type=str, default='0')
    parser.add_argument('--token', type=str, default='0')

    args = parser.parse_args()
    
    version = args.version
    username = args.username
    uuid = args.uuid
    userType = args.userType
    token = args.token

    # download_and_run(version, username, uuid, userType, token)
    start_custom_version(version, "1.8.9", username)