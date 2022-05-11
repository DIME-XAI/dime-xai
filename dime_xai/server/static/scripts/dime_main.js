var mini = true;

function toggleSidebar() {
    if (mini) {
        console.log("opening sidebar");
        document.getElementById("mySidebar").style.width = "250px";
        document.getElementById("main").style.marginLeft = "250px";
        document.getElementById("main").style.paddingLeft = "35px";
        $(".icon-text").removeClass("invisible");
        // $(".img-logo").attr("src", "../../static/images/dime_212121_n.png")
        this.mini = false;
    } else {
        console.log("closing sidebar");
        document.getElementById("mySidebar").style.width = "85px";
        document.getElementById("main").style.marginLeft = "85px";
        document.getElementById("main").style.paddingLeft = "36px";
        $(".icon-text").addClass("invisible");
        // $(".img-logo").attr("src", "../../static/images/dime_light_n.png")
        this.mini = true;
    }
}