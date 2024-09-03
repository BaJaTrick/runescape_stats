document.addEventListener("DOMContentLoaded", function() {
    const skillsTab = document.querySelector(".skills-tab");
    const questsTab = document.querySelector(".quests-tab");
    
    skillsTab.addEventListener("click", function() {
        document.getElementById("current_tab").value = "skills";
    });
    
    questsTab.addEventListener("click", function() {
        document.getElementById("current_tab").value = "quests";
    });
});
