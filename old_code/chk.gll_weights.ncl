begin
    
    np = 4

    gp = new(np,double)

    gp(0) = 0.166666666666667
    gp(1) = 0.833333333333333
    gp(2) = 0.833333333333333
    gp(3) = 0.166666666666667

    ; gp = gp / 2.

    gp_sum = new(1,double)
    gp_sum = 0.

    do i = 0,np-1
    do j = 0,np-1
        gp_sum = gp_sum + gp(i)*gp(j) 
    end do
    end do

    print(gp_sum)

end