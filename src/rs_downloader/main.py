import asyncio
import os
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from rs_downloader import bss
from rs_downloader.context_manage import go_and_back, open_json


async def iterate_project_list(page):
    """
    Root pageからproject listを取得する
    :param page:
    :return:
    """
    projects = []
    n_projects = 0
    while n_projects == 0:
        projects = await page.get_by_test_id("project-grid-card").all()
        n_projects = len(projects)
    for project in projects:
        yield (
            project,
            bss.extract_project(
                BeautifulSoup(await project.inner_html(), "html.parser")
            ),
        )


async def iterate_recordings(page, n_records: int):
    """
    Root pageからrecord listを取得する
    :param page:
    :param n_records:
    :return:
    """

    while True:
        locators = await page.locator(".MuiBox-root.css-10nxsnb.e1de0imv0").all()
        if len(locators) == n_records:
            break
    for record in locators:
        yield (
            record,
            bss.extract_recording(
                BeautifulSoup(await record.inner_html(), "html.parser")
            ),
        )


async def download_recordings(page, dst_dir: str):
    await page.wait_for_load_state("load")
    # await page.wait_for_timeout(5000)
    await page.get_by_role("button", name="High quality", exact=True).all()
    download_section = None
    while not download_section:
        download_section = await page.locator(
            ".MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation0"
        ).all()
        section_text = await asyncio.gather(
            *[section.text_content() for section in download_section]
        )
        filter_sections = ["All participants", "Transcript", "AI Voice"]
        # 不要なセクションを除外
        download_candidates = list(
            filter(
                lambda section: all(
                    map(lambda word: word not in section[1], filter_sections)
                ),
                enumerate(section_text),
            )
        )
        # print("n download buttons", len(download_candidates))
        if not download_candidates:
            await page.wait_for_timeout(1000)
    for idx, _button_text in download_candidates:
        section = download_section[idx]
        download_button = section.get_by_role("button", name="High quality", exact=True)
        await download_button.first.click()
        # Open Menu for Download
        aligned_audio = page.get_by_role("menuitem", name="Aligned audio WAV")
        async with page.expect_download() as download_info:
            await aligned_audio.click()
        download = await download_info.value
        download_path = os.path.join(dst_dir, download.suggested_filename)
        await download.save_as(download_path)
        yield download_path


async def main(
    projects_url: str,
    parent_dir: str,
    memo_path: str = "memo.json",
    timeout: int = 30 * 1000,
    strft: str = "%Y/%m/%d",
):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        )
        context.set_default_timeout(timeout=timeout)

        page = await context.new_page()
        # Go to list projects
        await page.goto(projects_url)
        await page.wait_for_load_state("load")
        print(f"Download Dir: {Path(parent_dir).absolute().as_uri()}")
        async for project, project_data in iterate_project_list(page):
            async with go_and_back(page, project.click, wait_time=1000) as page:
                n_records = project_data["recordings"]
                print("now in project:", project_data)
                project_url = page.url
                async for record, record_data in iterate_recordings(page, n_records):
                    async with go_and_back(page, record.click, wait_time=1000) as page:
                        with open_json(memo_path) as memo:
                            record_url = page.url
                            if project_url in memo and memo[project_url].get(
                                "complete", False
                            ):
                                print("Current Latest Project is downloaded.so end.")
                                return
                            print("now in record:", record_data)
                            # parent_dir/year/month/day/title/file_name に保存
                            dst_dir = (
                                Path(parent_dir)
                                / record_data["recorded_date"].strftime(strft)
                                / record_data["title"]
                            )
                            if not dst_dir.exists():
                                dst_dir.mkdir(parents=True, exist_ok=True)
                            async for download_path in download_recordings(
                                page, dst_dir
                            ):
                                print("downloaded to ", download_path)
                            if project_url not in memo:
                                memo[project_url] = {}
                            memo[project_url][record_url] = True
                with open_json(memo_path) as memo:
                    memo[project_url]["complete"] = True
