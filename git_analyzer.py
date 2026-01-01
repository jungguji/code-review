import subprocess
import os
from enum import Enum


class DiffMode(Enum):
    """Git diff 모드 설정"""
    UNSTAGED = "unstaged"      # git diff (워킹 디렉토리 변경사항만)
    STAGED = "staged"          # git diff --cached (staged 변경사항만)
    ALL = "all"                # git diff HEAD (staged + unstaged)
    BRANCH = "branch"          # git diff branch1..branch2
    COMMIT = "commit"          # git diff commit1..commit2


class GitManager:
    """Git diff 및 파일 분석 - 할루시네이션 방지를 위해 전체 코드도 함께 로드"""

    def __init__(
        self,
        extensions: tuple[str, ...] = ('.java', '.py', '.kt', '.js', '.ts'),
        diff_mode: DiffMode = DiffMode.ALL,
        base_ref: str | None = None,
        target_ref: str | None = None
    ):
        self.extensions = extensions
        self.diff_mode = diff_mode
        self.base_ref = base_ref
        self.target_ref = target_ref

    def _build_diff_command(self, file_path: str | None = None) -> list[str]:
        """diff 모드에 따른 git 명령어 생성"""
        cmd = ["git", "diff"]

        if self.diff_mode == DiffMode.STAGED:
            cmd.append("--cached")
        elif self.diff_mode == DiffMode.ALL:
            cmd.append("HEAD")
        elif self.diff_mode in (DiffMode.BRANCH, DiffMode.COMMIT):
            if self.base_ref and self.target_ref:
                cmd.append(f"{self.base_ref}..{self.target_ref}")
            elif self.base_ref:
                cmd.append(self.base_ref)
        # UNSTAGED는 추가 인자 없음

        if file_path:
            cmd.extend(["--", file_path])

        return cmd

    def get_diff_files(self) -> list[str]:
        """변경된 파일 목록 추출 (소스코드만 필터링)"""
        cmd = self._build_diff_command()
        cmd.append("--name-only")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return [
            f for f in result.stdout.split('\n')
            if f and f.endswith(self.extensions)
        ]

    def get_file_content(self, file_path: str) -> str:
        """파일 전체 내용 로드"""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def get_diff_context(self, file_path: str) -> str:
        """특정 파일의 diff 내용만 추출"""
        cmd = self._build_diff_command(file_path)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout

    def get_project_structure(self) -> str:
        """
        git ls-files를 활용한 프로젝트 구조 반환
        .gitignore 자동 적용, Spring (Java/Kotlin) 프로젝트 지원
        """
        # 소스코드 + 설정 파일 확장자
        include_exts = {
            '.java', '.kt',                    # Java/Kotlin
            '.xml', '.yml', '.yaml',           # 설정 (pom.xml, application.yml)
            '.properties',                     # Spring 설정
            '.gradle', '.kts',                 # Gradle 빌드
            '.py', '.js', '.ts'                # 기타
        }

        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True,
            text=True
        )

        files = [
            f for f in result.stdout.split('\n')
            if f and any(f.endswith(ext) for ext in include_exts)
        ]

        return '\n'.join(sorted(files))