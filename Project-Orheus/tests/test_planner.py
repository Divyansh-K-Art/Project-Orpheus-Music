import pytest
from planner import plan_song, MusicPlanner


def test_plan_song_structure():
    prompt = "a chill lo-fi love song with acoustic guitar"
    plan = plan_song(prompt)
    # Expected keys
    expected_keys = {"structure", "tempo", "key", "instruments", "section_lengths"}
    assert set(plan.keys()) == expected_keys
    # Tempo should be slow (<= 90)
    assert plan["tempo"] <= 90
    # Instruments should include acoustic guitar or piano
    assert any(inst in plan["instruments"] for inst in ["acoustic guitar", "piano"])
    # Structure should contain at least Intro and Outro
    assert "Intro" in plan["structure"] and "Outro" in plan["structure"]


def test_plan_song_energetic():
    prompt = "energetic pop dance tune with synth and drum machine"
    plan = plan_song(prompt)
    # Tempo should be fast (>= 130)
    assert plan["tempo"] >= 130
    # Instruments should include synth
    assert "synth" in plan["instruments"]


def test_music_planner_wrapper():
    planner = MusicPlanner()
    plan = planner.plan("happy acoustic guitar melody")
    assert isinstance(plan, dict)
    assert "structure" in plan
    assert "tempo" in plan
