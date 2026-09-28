import os

EXAMPLE_FILE = '.env.example'
ENV_FILE = '.env'

def main():
    if not os.path.exists(EXAMPLE_FILE):
        print(f"오류: '{EXAMPLE_FILE}' 파일을 찾을 수 없습니다.")
        return
    if os.path.exists(ENV_FILE):
        overwrite = input(f"⚠️ '{ENV_FILE}' 파일이 이미 존재합니다. 덮어쓰시겠습니까? (y/N): ")
        if overwrite.lower() != 'y':
            print("작업을 취소합니다.")
            return
    with open(EXAMPLE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_env_lines = []
    print("\n=== 🛠️ .env 파일 세팅을 시작합니다 ===")
    print("(엔터를 누르면 괄호 안의 기본값이 들어갑니다)\n")
    
    for line in lines:
        line = line.strip()
        
        if not line or line.startswith('#'):
            new_env_lines.append(line)
            continue
        
        if '=' in line:
            key, default_val = line.split('=', 1)
            user_input = input(f"{key} [{default_val}]: ")
            final_val = user_input if user_input.strip() else default_val
            new_env_lines.append(f"{key}={final_val}")
        else:
            new_env_lines.append(line)
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_env_lines) + '\n')
    print(f"\n성공적으로 '{ENV_FILE}' 파일이 생성되었습니다!")


if __name__ == '__main__':
    main()
